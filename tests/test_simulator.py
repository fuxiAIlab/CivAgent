import os

import civsim.simulator.simulator as simulator


def test_simulator():
    simulator.init_jvm()
    path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "scripts", "reproductions", "Autosave-China-60"
    )
    simulator.run(path, 10, False, False, False)
    # simulator.run(path, 10, True, True, True)
    simulator.run_hasAtLeastMotivationToAttack(path, "China", "Aztecs")
    simulator.run_canSignResearchAgreementsWith(path, "China", "Aztecs")
    simulator.run_wantsToSignDefensivePact(path, "China", "Aztecs")
    simulator.run_hasAtLeastMotivationToAttackScore(path, "China", "Aztecs")
    assert True
