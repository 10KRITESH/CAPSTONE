// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

/**
 * @title GovernanceAudit
 * @dev Permissioned Blockchain Governance & Tamper-Evident Audit Record Store
 *      for Adaptive Reputation-Based Secure Federated IDS.
 */
contract GovernanceAudit {

    address public owner;
    mapping(address => bool) public authorizedCoordinators;
    mapping(bytes32 => bool) public registeredParticipants;

    struct AuditDecision {
        uint256 roundId;
        bytes32 clientHash;
        bytes32 oldState;
        bytes32 newState;
        uint256 evidenceScore; // scaled by 1e4 (e.g. 0.70 -> 7000)
        bytes32 recordHash;
        uint256 blockTimestamp;
    }

    mapping(bytes32 => AuditDecision) private decisions;
    bytes32[] public decisionHashes;

    event CoordinatorAuthorized(address indexed coordinator);
    event ParticipantRegistered(bytes32 indexed clientHash);
    event DecisionRecorded(
        uint256 indexed roundId,
        bytes32 indexed clientHash,
        bytes32 recordHash,
        bytes32 newState
    );

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform action");
        _;
    }

    modifier onlyCoordinator() {
        require(authorizedCoordinators[msg.sender] || msg.sender == owner, "Not authorized coordinator");
        _;
    }

    constructor() {
        owner = msg.sender;
        authorizedCoordinators[msg.sender] = true;
    }

    function authorizeCoordinator(address coordinator) external onlyOwner {
        authorizedCoordinators[coordinator] = true;
        emit CoordinatorAuthorized(coordinator);
    }

    function registerParticipant(bytes32 clientHash) external onlyCoordinator {
        registeredParticipants[clientHash] = true;
        emit ParticipantRegistered(clientHash);
    }

    function recordDecision(
        uint256 roundId,
        bytes32 clientHash,
        bytes32 oldState,
        bytes32 newState,
        uint256 evidenceScore,
        bytes32 recordHash
    ) external onlyCoordinator {
        require(decisions[recordHash].roundId == 0, "Decision record hash already exists");

        decisions[recordHash] = AuditDecision({
            roundId: roundId,
            clientHash: clientHash,
            oldState: oldState,
            newState: newState,
            evidenceScore: evidenceScore,
            recordHash: recordHash,
            blockTimestamp: block.timestamp
        });

        decisionHashes.push(recordHash);
        emit DecisionRecorded(roundId, clientHash, recordHash, newState);
    }

    function getDecision(bytes32 recordHash)
        external
        view
        returns (
            uint256 roundId,
            bytes32 clientHash,
            bytes32 oldState,
            bytes32 newState,
            uint256 evidenceScore,
            uint256 blockTimestamp
        )
    {
        AuditDecision memory d = decisions[recordHash];
        require(d.roundId != 0, "Record not found");
        return (d.roundId, d.clientHash, d.oldState, d.newState, d.evidenceScore, d.blockTimestamp);
    }

    function getDecisionCount() external view returns (uint256) {
        return decisionHashes.length;
    }
}
