# install java on linux
apt install ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /etc/apt/keyrings/adoptium.gpg
chmod a+r /etc/apt/keyrings/adoptium.gpg
echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list
apt update -y
apt install temurin-21-jdk

wget https://mirrors.tuna.tsinghua.edu.cn/anaconda/miniconda/Miniconda3-py38_23.11.0-1-Linux-x86_64.sh
bash Miniconda3-py38_23.11.0-1-Linux-x86_64.sh -b -p /root/miniconda3
source ~/.bashrc
source /root/miniconda3/etc/profile.d/conda.sh

conda create --name unciv python=3.9 --yes
source /root/miniconda3/etc/profile.d/conda.sh && conda activate unciv && python --version

pip install -r requirements.txt

#linux
curl -fsSL https://ollama.com/install.sh | sh
nohup ollama serve &
ollama pull mistral
ollama pull llama3
ollama pull gemma
