#!/usr/bin/env python3
# copy from https://github.com/Mape6/Unciv_server
import http.server
import socketserver
import os
import re
import logging
from civsim import logger
import socket
import urllib.request
from datetime import datetime
from http import HTTPStatus
from civsim import utils
from deployment import redis_mq
from civagent.config import config_data

mq = redis_mq.RedisStreamMQ()


port = config_data['unciv_server']['port']
# 'Writes separate logfiles for each game'
game_logfiles = True
# parser = argparse.ArgumentParser(description='This is a simple HTTP webserver for Unciv')
#
# parser.add_argument('-p', '--port',
#                     action='store',
#                     default='80',
#                     type=int,
#                     help='Specifies the port on which the server should listen (default: %(default)s)'
#                     )
# parser.add_argument('-g', '--game-logfiles',
#                     action='store_true',
#                     help='Writes separate logfiles for each game'
#                     )
# parser.add_argument('-l', '--log-level',
#                     default='WARNING',
#                     choices=['CRITICAL', 'ERROR', 'WARNING', 'INFO', 'DEBUG'],
#                     help='Change logging level (default: %(default)s)'
#                     )
#
# args = parser.parse_args()
#
# if 1 <= args.port <= 65535:
#     port = args.port
# else:
#     parser.error('Port needs to be an integer between 1 and 65535')

# logging.basicConfig(level=args.log_level, format='%(asctime)s - %(levelname)s - %(message)s')

regex_uuid = '[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}'
regex_path = '/files/'
regex_user_agent = 'Unciv/.*-GNU-Terry-Pratchett'

suffix_preview_file = '_Preview'
suffix_lock_file = '_Lock'
suffixes_list = [suffix_preview_file, suffix_lock_file]

regexc_main_game_file = re.compile(rf'^{regex_path}{regex_uuid}$')
regexc_preview_file = re.compile(rf'^{regex_path}{regex_uuid}{suffix_preview_file}$')
regexc_lock_file = re.compile(rf'^{regex_path}{regex_uuid}{suffix_lock_file}$')
regexc_all_game_files = re.compile(rf'^{regex_path}{regex_uuid}({suffix_preview_file}|{suffix_lock_file}|$)$')
regexc_user_agent = re.compile(regex_user_agent)

max_path_length = 128
max_content_length = 5242880  # (5 MB is really enough)
log_files_folder = '/logs/'
log_time_format = '%Y-%m-%d %H:%M:%S.%f'


class MyHttpRequestHandler(http.server.SimpleHTTPRequestHandler):

    def is_gameid(self, text):
        text = text.strip()
        pattern = r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}'
        result = re.findall(pattern, text)
        if len(result)>0 and len(result[0])==36:
            return result[0]
        return ''

    def get_game_infos(self, file_path):
        save_data = utils.get_latest_savefile(file_path)
        language = save_data['gameParameters'].get('language', '')
        llm_api_key = save_data['gameParameters'].get('llm_api_key', '')
        llm_model = save_data['gameParameters'].get('llm_model', '')
        player_civ = [civ.get('civName', '').lower() for civ in save_data.get('civilizations', []) if 'playerId' in civ]
        civs = [civ.get('civName', '').lower() for civ in save_data.get('civilizations', []) if 'playerId' not in civ]
        robot_civs = [civ_name for civ_name in civs if civ_name!='barbarians']
        return player_civ, robot_civs, save_data.get("turns", 1), language, llm_api_key, llm_model

    def logger_in_redis(self, filename):
        if 'Preview' in filename:
            game_id = self.is_gameid(filename)
            if game_id and mq.redis.exists(game_id):
                mq.redis.expire(game_id, 60)
                logger.debug(f'Refresh {game_id} in redis.')
        else:
            logger.info(f'{filename} enter in logger_in_redis.')
            game_id = self.is_gameid(filename)
            if game_id:
                player_civ, robot_civs, turns, language, llm_api_key, llm_model = self.get_game_infos(filename)
                info = {
                    'player_civ': player_civ, 'civ_robots': robot_civs,
                    'turns': turns, 'language': language,
                    'llm_api_key':llm_api_key, 'llm_model':llm_model
                }
                mq.set('gameid2info_' + game_id, info)
                mq.set(game_id, info, expiration_time=60 * 10)
                logger.info(f'Set {game_id} : {info} in redis.')
                # event trigger: next_turn
                mq.xadd(
                    game_id,
                    {
                        "game_id": game_id,
                        "type": "next_turn",
                        "turns": turns,
                        "addTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }
                )

    def write_to_log_file(self, path, log_entry):
        # Create timestamp and add it as prefix to log_entry
        log_entry = datetime.now().strftime(log_time_format) + ' - ' + log_entry
        # Remove any suffix from filename to get only UUID
        for suffix in suffixes_list:
            path = path.strip(suffix)
        # Get only the filename
        log_file = os.path.basename(path)
        # Join log path and log filename
        log_file_path = os.path.join(log_files_folder, log_file)
        # Check if log path exists
        if not os.path.exists(log_files_folder):
            try:
                os.makedirs(log_files_folder)
                logger.debug(f'Folder {log_files_folder} created.')
            # If dir could not be created -> log the exception and send 500 Internal Server Error
            except Exception as e:
                logger.exception(f'Folder {log_files_folder} could not be created. Exception: {e}', exc_info=True)

        # Write log_entry to file
        try:
            with open(log_file_path, 'a') as f:
                f.write(log_entry)
            logger.debug(f'Logfile {log_file_path} updated successfully.')
        # If file could not be updated -> log the exception
        except Exception as e:
            logger.exception(f'Logfile {log_file_path} could not be updated. Exception: {e}', exc_info=True)

    def send_file_content(self, path, client_ip):
        try:
            with open(path, 'r') as save_file:
                file_content = save_file.read()
            http_status = HTTPStatus.OK
            log_entry = f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}'
            logger.debug(log_entry)
            self.send_response_only(http_status)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(file_content.encode())
            if game_logfiles:
                self.write_to_log_file(path, f'{log_entry}\n')
            self.logger_in_redis(path)
        except FileNotFoundError:
            http_status = HTTPStatus.NOT_FOUND
            logger.debug(
                f'Client: {client_ip}, Request: "{self.requestline}", HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    def write_file_content(self, path, content_length, client_ip):
        # If the dir does not exist -> create it
        if not os.path.exists(os.path.dirname(path)):
            try:
                os.makedirs(os.path.dirname(path))
                logger.debug(f'Path {os.path.dirname(path)} created.')
            # If dir could not be created -> log the exception and send 500 Internal Server Error
            except Exception as e:
                logger.exception(f'Path {os.path.dirname(path)} could not be created. Exception: {e}', exc_info=True)
                http_status = HTTPStatus.INTERNAL_SERVER_ERROR
                logger.exception(
                    f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                self.send_response_only(http_status)
                self.end_headers()

        # Write content to file
        try:
            with open(path, 'wb') as f:
                f.write(self.rfile.read(content_length))
            http_status = HTTPStatus.CREATED
            log_entry = f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}'
            logger.debug(log_entry)
            self.send_response_only(http_status)
            self.end_headers()
            if game_logfiles:
                self.write_to_log_file(path, f'{log_entry}\n')
        # If file could not be created -> log the exception and send 500 Internal Server Error
        except Exception as e:
            logger.exception(f'File {path} could not be created. Exception: {e}', exc_info=True)
            http_status = HTTPStatus.INTERNAL_SERVER_ERROR
            logger.exception(
                f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    def delete_file(self, path, client_ip):
        if os.path.exists(path):
            os.remove(path)
            http_status = HTTPStatus.OK
            log_entry = f'Client: {client_ip}, Request: "{self.requestline}", HTTP_status_code: {http_status} {http_status.phrase}'
            logger.debug(log_entry)
            self.send_response_only(http_status)
            self.end_headers()
            if game_logfiles:
                self.write_to_log_file(path, f'{log_entry}\n')
        else:
            http_status = HTTPStatus.NOT_FOUND
            logger.warning(
                f'Client: {client_ip}, Request: "{self.requestline}", HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    # Sync the server archive to the game, within the turn.
    def do_GET(self):
        # Check if X-Forwarded-For is present in headers -> use client IP out of it
        if self.headers['X-Forwarded-For']:
            client_ip = self.headers['X-Forwarded-For']
        else:
            client_ip = self.address_string()

        # Check if User-Agent is from Unciv in headers -> allow answers, otherwise send 403 FORBIDDEN
        if not regexc_user_agent.search(self.headers['User-Agent']):
            http_status = HTTPStatus.FORBIDDEN
            logger.warning(
                f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase} wrong User-Agent {self.headers["User-Agent"]}')
            self.send_response_only(http_status)
            self.end_headers()

        # Check path for game file names -> send file content
        elif regexc_all_game_files.search(self.path):
            path = self.translate_path(self.path)
            # Preview or main file
            self.send_file_content(path, client_ip)

        # Check for connection check and response with 'true'
        elif self.path.endswith('isalive'):
            http_status = HTTPStatus.OK
            logger.debug(
                f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write("true".encode())

        # Everything else is not allowed
        else:
            http_status = HTTPStatus.FORBIDDEN
            logger.warning(
                f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    # Synchronize the game archive to the server,
    # but do not trigger it right after the player's turn ends;
    # instead, wait until all civs are completed.
    def do_PUT(self):
        # Check if X-Forwarded-For is present in headers -> use client IP out of it
        if self.headers['X-Forwarded-For']:
            client_ip = self.headers['X-Forwarded-For']
        else:
            client_ip = self.address_string()

        # Check if path is not too long
        if len(self.path) <= max_path_length:
            # Check if Content-Length is not too big
            if int(self.headers['Content-Length']) <= max_content_length:
                content_length = int(self.headers['Content-Length'])

                # Check path for preview file name
                if regexc_preview_file.search(self.path):
                    path = self.translate_path(self.path)
                    self.write_file_content(path, content_length, client_ip)

                # Check path for main game file name
                elif regexc_main_game_file.search(self.path):
                    path = self.translate_path(self.path)
                    self.write_file_content(path, content_length, client_ip)
                    logger.info(f'put {self.path}')
                    self.logger_in_redis(path)

                # Check path for lock file name
                elif regexc_lock_file.search(self.path):
                    path = self.translate_path(self.path)
                    self.write_file_content(path, content_length, client_ip)

                # If path does not have the right file names -> send 403 FORBIDDEN
                else:
                    http_status = HTTPStatus.FORBIDDEN
                    logger.warning(
                        f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                    self.send_response_only(http_status)
                    self.end_headers()

            # If Content-Length is too long -> send 400 BAD REQUEST
            else:
                http_status = HTTPStatus.BAD_REQUEST
                logger.warning(
                    f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                self.send_response_only(http_status)
                self.end_headers()
        # If path length is too long -> send 400 BAD REQUEST
        else:
            http_status = HTTPStatus.BAD_REQUEST
            logger.warning(
                f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()

    def do_DELETE(self):
        # Check if X-Forwarded-For is present in headers -> use client IP out of it
        if self.headers['X-Forwarded-For']:
            client_ip = self.headers['X-Forwarded-For']
        else:
            client_ip = self.address_string()

        # Check if path is not too long
        if len(self.path) <= max_path_length:

            # Check path for game file names
            if regexc_all_game_files.search(self.path):
                path = self.translate_path(self.path)
                self.delete_file(path, client_ip)

            # If path does not have the right file names -> send 403 FORBIDDEN
            else:
                http_status = HTTPStatus.FORBIDDEN
                logger.warning(
                    f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
                self.send_response_only(http_status)
                self.end_headers()

        # If path length is too long -> send 400 BAD REQUEST
        else:
            http_status = HTTPStatus.BAD_REQUEST
            logger.warning(
                f'Client: {client_ip}, Request: "{self.requestline}" HTTP_status_code: {http_status} {http_status.phrase}')
            self.send_response_only(http_status)
            self.end_headers()


def get_private_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't have to be reachable
        s.connect(('10.254.254.254', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip


def get_public_ip():
    ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
    return ip


Handler = MyHttpRequestHandler

try:
    with socketserver.TCPServer(("", port), Handler) as httpd:
        private_ip = get_private_ip()

        try:
            public_ip = get_public_ip()
            public_url = f'http://{public_ip}'
        except:
            public_url = None

        private_url = f'http://{private_ip}'

        if port != 80:
            private_url += f':{port}'
            if public_url:
                public_url += f':{port}'

        print(f'Try the following URLs in Unciv to connect with this server.')
        print(f'From LAN network: {private_url}')
        if public_url:
            print(f'From internet: {public_url}')

        httpd.serve_forever()
except OSError as error:
    if error.errno == 10048:
        logger.exception(f'Port {port} is already used by any other service!')
    else:
        print(error)
except BaseException as e:
    print(e)
