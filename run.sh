#!/usr/bin/env bash
# ==============================================================================
# 🛡️ Secure Federated Learning IDS with Blockchain Governance — Master Runner
# ==============================================================================
# Usage:
#   ./run.sh              # Interactive menu / default full demonstration
#   ./run.sh --demo       # Run 6-Stage SMOKE TEST (single seed, 5 rounds)
#   ./run.sh --reset-state # Clean reset of demo audit.db and blockchain_ledger.json
#   ./run.sh --dashboard  # Launch Streamlit Web Dashboard
#   ./run.sh --all        # Run Smoke Test + Generate Plots + Launch Dashboard
#   ./run.sh --ablation   # Run 8-Way Defense Shootout Benchmark
#   ./run.sh --verify     # Run Cryptographic Blockchain Tamper Verification
# ==============================================================================

set -eo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for terminal styling
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

echo -e "${CYAN}${BOLD}"
echo "=============================================================================="
echo " 🛡️  SECURE FEDERATED LEARNING IDS & BLOCKCHAIN GOVERNANCE SUITE"
echo "=============================================================================="
echo -e "${NC}"

# 1. Locate Virtual Environment Python & Streamlit
VENV_DIR="$SCRIPT_DIR/.venv"
if [ -f "$VENV_DIR/bin/python" ]; then
    PYTHON_BIN="$VENV_DIR/bin/python"
    STREAMLIT_BIN="$VENV_DIR/bin/streamlit"
else
    echo -e "${YELLOW}[!] .venv not found in project root. Checking system python3...${NC}"
    if command -v python3 &>/dev/null; then
        PYTHON_BIN="python3"
        STREAMLIT_BIN="streamlit"
    else
        echo -e "${RED}[ERROR] Python 3 not found. Please setup .venv with dependencies.${NC}"
        exit 1
    fi
fi

# 2. Check Hardware Acceleration
echo -e "${CYAN}🔍 Checking Hardware & Environment...${NC}"
$PYTHON_BIN -c "
import torch
print('   • Python:', torch.sys.version.split()[0])
print('   • PyTorch:', torch.__version__)
if torch.cuda.is_available():
    print('   • Hardware Acceleration: [ENABLED] GPU ->', torch.cuda.get_device_name(0))
else:
    print('   • Hardware Acceleration: [DISABLED] Running on CPU')
"

# 3. Check Dataset & Partitions
DEV_DATA="$SCRIPT_DIR/data/processed/dev/server_val.parquet"
CLIENT_PARTITIONS="$SCRIPT_DIR/data/partitions/dev/client_00.parquet"

if [ ! -f "$DEV_DATA" ] || [ ! -f "$CLIENT_PARTITIONS" ]; then
    echo -e "\n${YELLOW}⚠️ Preprocessed datasets or client partitions not detected.${NC}"
    echo -e "${CYAN}⚙️ Automatically generating dev datasets and Non-IID partitions...${NC}"
    $PYTHON_BIN src/data/preprocess.py --dev
    $PYTHON_BIN src/data/partition.py --dev
    echo -e "${GREEN}✓ Dataset preprocessing and partitioning complete.${NC}"
else
    echo -e "   • Dataset: dev partitions & server validation [READY]"
fi

echo ""

# Functions for modes
run_master_demo() {
    echo -e "${GREEN}${BOLD}🚀 Executing 6-Stage Smoke Test Suite (5 rounds, single seed)...${NC}\n"
    $PYTHON_BIN src/experiments/master_demo.py
}

reset_demo_state() {
    echo -e "${YELLOW}${BOLD}🧹 Resetting demo audit database and blockchain ledger...${NC}"
    rm -f data/audit.db data/blockchain_ledger.json data/test_audit.db
    echo -e "${GREEN}✓ Clean demo state initialized.${NC}\n"
}

run_dashboard() {
    echo -e "${GREEN}${BOLD}🌐 Launching Interactive Streamlit Dashboard...${NC}"
    echo -e "${CYAN}Access the dashboard in your browser (usually http://localhost:8501)${NC}\n"
    $STREAMLIT_BIN run dashboard/app.py
}

run_ablation() {
    echo -e "${GREEN}${BOLD}📊 Executing 8-Way Defense & Ablation Shootout...${NC}\n"
    $PYTHON_BIN src/experiments/ablation.py
}

run_tamper_verification() {
    echo -e "${GREEN}${BOLD}⛓️ Executing Blockchain Tamper Verification Engine Test...${NC}\n"
    $PYTHON_BIN src/audit/verification.py
}

run_sim() {
    shift 1 || true
    echo -e "${GREEN}${BOLD}⚔️ Launching Terminal Adversarial FL Simulator...${NC}\n"
    $PYTHON_BIN src/experiments/quick_sim.py "$@"
}

run_plots() {
    echo -e "${GREEN}${BOLD}📈 Generating Publication-Quality Benchmark Plots...${NC}\n"
    $PYTHON_BIN src/experiments/generate_plots.py
}

run_all() {
    run_master_demo
    run_plots
    echo -e "\n${GREEN}${BOLD}✓ Master demo and plot generation finished successfully!${NC}"
    echo -e "${CYAN}Launching Streamlit dashboard now...${NC}\n"
    run_dashboard
}

# Mode selection based on argument
MODE="${1:-}"

case "$MODE" in
    --reset-state|reset-state|reset)
        reset_demo_state
        exit 0
        ;;
    --results|results)
        shift
        TARGET_RUN_ID="${1:-step_d_evaluate}"
        shift || true
        $PYTHON_BIN src/experiments/aggregate_results.py --run-dir "results/runs/$TARGET_RUN_ID" "$@"
        exit 0
        ;;
    --sim|sim)
        run_sim "$@"
        exit 0
        ;;
    --demo|demo)
        run_master_demo
        exit 0
        ;;
    --dashboard|--ui|dashboard|ui)
        run_dashboard
        exit 0
        ;;
    --all|all|full)
        run_all
        exit 0
        ;;
    --ablation|ablation)
        run_ablation
        exit 0
        ;;
    --verify|verify|blockchain)
        run_tamper_verification
        exit 0
        ;;
    --plots|plots)
        run_plots
        exit 0
        ;;
    --help|-h|help)
        echo -e "${BOLD}Available commands:${NC}"
        echo "  ./run.sh              Interactive menu / run full demonstration"
        echo "  ./run.sh sim [args]   Run Terminal Adversarial FL Simulator (e.g. -a targeted -d shootout -r 5)"
        echo "  ./run.sh all          Run Master Demo + Generate Plots + Launch Dashboard"
        echo "  ./run.sh demo         Run 6-Stage Master Demonstration suite"
        echo "  ./run.sh dashboard    Launch Streamlit Interactive Web Dashboard"
        echo "  ./run.sh ablation     Run 8-Way Defense Shootout Benchmark"
        echo "  ./run.sh verify       Run Blockchain & Tamper Verification Engine"
        echo "  ./run.sh plots        Re-generate Benchmark Plots & Visualizations"
        exit 0
        ;;
    "")
        # Interactive Menu if TTY, or default to all
        if [ -t 0 ]; then
            echo -e "${BOLD}Select what you would like to run:${NC}"
            echo -e "  ${CYAN}1)${NC} ${BOLD}Run 6-Stage Master Demonstration${NC} (Centralized baseline, Non-IID, Clean FL, Defense Shootout, Blockchain, Overhead)"
            echo -e "  ${CYAN}2)${NC} ${BOLD}Launch Streamlit Web Dashboard${NC} (Live GUI, Tamper Sandbox, Reputation Heatmaps)"
            echo -e "  ${CYAN}3)${NC} ${BOLD}Run Terminal Adversarial Simulator${NC} (Interactive CLI FL Shootout)"
            echo -e "  ${CYAN}4)${NC} ${BOLD}Run Full Suite + Launch Dashboard${NC} (Demo -> Plots -> Dashboard)"
            echo -e "  ${CYAN}5)${NC} ${BOLD}Run 8-Way Defense Ablation Shootout${NC} (FedAvg vs Krum vs Trimmed Mean vs Proposed)"
            echo -e "  ${CYAN}6)${NC} ${BOLD}Run Blockchain Tamper Verification Test${NC}"
            echo -e "  ${CYAN}7)${NC} Exit"
            echo ""
            read -r -p "Enter choice [1-7] (Default: 1): " CHOICE
            CHOICE="${CHOICE:-1}"

            case "$CHOICE" in
                1) run_master_demo ;;
                2) run_dashboard ;;
                3) run_sim sim ;;
                4) run_all ;;
                5) run_ablation ;;
                6) run_tamper_verification ;;
                7) echo "Exiting."; exit 0 ;;
                *) echo -e "${RED}Invalid choice. Exiting.${NC}"; exit 1 ;;
            esac
        else
            run_master_demo
        fi
        ;;
    *)
        echo -e "${RED}Unknown option: $MODE${NC}"
        echo "Run './run.sh --help' for usage instructions."
        exit 1
        ;;
esac
