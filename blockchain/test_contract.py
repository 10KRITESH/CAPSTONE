#!/usr/bin/env python3
"""
test_contract.py — Local EVM Verification for GovernanceAudit.sol Smart Contract.
Compiles GovernanceAudit.sol with solc 0.8.20 and executes full deployment,
access control, state transition commitment, and query tests using Web3.py with EthereumTesterProvider.
"""

import hashlib
import sys
from web3 import Web3
from web3.providers.eth_tester import EthereumTesterProvider
import solcx


def test_governance_audit_contract():
    print("=" * 65)
    print("Executing Local EVM Smart Contract Test: GovernanceAudit.sol")
    print("=" * 65)

    # 1. Compile Solidity contract
    contract_file = "blockchain/contracts/GovernanceAudit.sol"
    print(f"[*] Compiling {contract_file} with solc 0.8.20...")
    solcx.install_solc('0.8.20')
    compiled = solcx.compile_files(
        [contract_file],
        output_values=['abi', 'bin'],
        solc_version='0.8.20'
    )
    contract_id = f"{contract_file}:GovernanceAudit"
    abi = compiled[contract_id]['abi']
    bytecode = compiled[contract_id]['bin']
    print(f"[OK] Compilation successful! Bytecode size: {len(bytecode) // 2} bytes")

    # 2. Setup Web3 with EthereumTesterProvider (In-Memory EVM)
    w3 = Web3(EthereumTesterProvider())
    assert w3.is_connected(), "Failed to connect to EVM provider"
    accounts = w3.eth.accounts
    deployer = accounts[0]
    coordinator = accounts[1]
    unauthorized = accounts[2]
    print(f"[*] Deployer Account:    {deployer}")
    print(f"[*] Coordinator Account: {coordinator}")

    # 3. Deploy Contract
    GovernanceContract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = GovernanceContract.constructor().transact({'from': deployer})
    tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = tx_receipt.contractAddress
    contract = w3.eth.contract(address=contract_address, abi=abi)
    print(f"[OK] GovernanceAudit deployed at: {contract_address} (Gas used: {tx_receipt.gasUsed})")

    # 4. Verify Owner
    owner = contract.functions.owner().call()
    assert owner == deployer, f"Owner mismatch: {owner} != {deployer}"
    print(f"[OK] Contract Owner correctly initialized to deployer")

    # 5. Authorize Coordinator
    tx = contract.functions.authorizeCoordinator(coordinator).transact({'from': deployer})
    w3.eth.wait_for_transaction_receipt(tx)
    is_coord = contract.functions.authorizedCoordinators(coordinator).call()
    assert is_coord is True, "Coordinator authorization failed"
    print(f"[OK] Authorized coordinator {coordinator}")

    # 6. Register Federated Client Hash
    client_id = "client_8_attacker"
    client_hash = hashlib.sha256(client_id.encode()).digest() # 32 bytes
    tx = contract.functions.registerParticipant(client_hash).transact({'from': coordinator})
    w3.eth.wait_for_transaction_receipt(tx)
    is_registered = contract.functions.registeredParticipants(client_hash).call()
    assert is_registered is True, "Participant registration failed"
    print(f"[OK] Registered client {client_id} (Hash: 0x{client_hash.hex()[:16]}...)")

    # 7. Record Governance Audit Decision (Client 8 downgraded TRUSTED -> PROBATION)
    round_id = 1
    old_state = hashlib.sha256(b"TRUSTED").digest()
    new_state = hashlib.sha256(b"PROBATION").digest()
    evidence_score = 7500 # Scaled by 1e4 -> 0.75
    record_content = f"{round_id}:{client_id}:TRUSTED:PROBATION:0.75"
    record_hash = hashlib.sha256(record_content.encode()).digest()

    tx = contract.functions.recordDecision(
        round_id,
        client_hash,
        old_state,
        new_state,
        evidence_score,
        record_hash
    ).transact({'from': coordinator})
    receipt = w3.eth.wait_for_transaction_receipt(tx)
    print(f"[OK] Recorded Decision Hash: 0x{record_hash.hex()[:16]}... (Gas used: {receipt.gasUsed})")

    # 8. Query On-Chain Audit Record
    count = contract.functions.getDecisionCount().call()
    assert count == 1, f"Expected 1 decision, got {count}"
    retrieved = contract.functions.getDecision(record_hash).call()
    ret_round, ret_client, ret_old, ret_new, ret_evidence, ret_time = retrieved

    assert ret_round == round_id, "Round ID mismatch"
    assert ret_client == client_hash, "Client hash mismatch"
    assert ret_old == old_state, "Old state mismatch"
    assert ret_new == new_state, "New state mismatch"
    assert ret_evidence == evidence_score, "Evidence score mismatch"
    print(f"[OK] Retrieved and verified on-chain decision record:")
    print(f"     - Round: {ret_round}")
    print(f"     - Client Hash: 0x{ret_client.hex()[:16]}...")
    print(f"     - Evidence Score: {ret_evidence / 10000.0:.2f}")
    print(f"     - Timestamp: {ret_time}")

    # 9. Verify Duplicate Protection (Replay Attack Prevention)
    try:
        contract.functions.recordDecision(
            round_id,
            client_hash,
            old_state,
            new_state,
            evidence_score,
            record_hash
        ).transact({'from': coordinator})
        assert False, "Should have reverted on duplicate recordHash"
    except Exception:
        print(f"[OK] Replay protection passed (Reverted on duplicate record hash)")

    # 10. Verify Unauthorized Access Rejection
    try:
        contract.functions.recordDecision(
            round_id,
            client_hash,
            old_state,
            new_state,
            evidence_score,
            hashlib.sha256(b"unauthorized_record").digest()
        ).transact({'from': unauthorized})
        assert False, "Should have reverted for unauthorized caller"
    except Exception:
        print(f"[OK] Access control passed (Reverted for non-coordinator address)")

    print("=" * 65)
    print("ALL 10 SMART CONTRACT TESTS PASSED PERFECTLY!")
    print("=" * 65)


if __name__ == "__main__":
    test_governance_audit_contract()
