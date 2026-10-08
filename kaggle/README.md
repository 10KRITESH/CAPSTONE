# Kaggle Cloud GPU Setup & Execution Guide

This guide walks you through running your Capstone Federated Learning benchmarks on Kaggle's free **NVIDIA T4 GPUs (16 GB VRAM, 30 hrs/week free)**.

---

## Prerequisites (One-Time Setup)

### 1. Get your free Kaggle API Token
1. Log in to [kaggle.com](https://www.kaggle.com).
2. Go to **Settings** (`https://www.kaggle.com/settings`).
3. Scroll down to the **API** section and click **"Create New Token"**.
4. This downloads a file named `kaggle.json`.

### 2. Install & Configure Kaggle CLI on your laptop
Run these commands in your terminal:
```bash
# 1. Install the Kaggle CLI
pip install kaggle

# 2. Place kaggle.json in ~/.kaggle/
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json

# 3. Verify it works
kaggle datasets list
```

---

## How to Run from Local Terminal (Method A: Kaggle CLI)

1. Open [`kaggle/kernel-metadata.json`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/kaggle/kernel-metadata.json) and replace `INSERT_YOUR_KAGGLE_USERNAME` with your real Kaggle username (found at kaggle.com).
2. Push and launch execution on Kaggle GPU:
   ```bash
   kaggle kernels push -p ./kaggle
   ```
3. Check the live execution status:
   ```bash
   kaggle kernels status YOUR_USERNAME/capstone-fl-benchmark
   ```
4. Once completed, download the resulting reports and benchmark tables back to your laptop:
   ```bash
   kaggle kernels output YOUR_USERNAME/capstone-fl-benchmark -p ./results_from_cloud/
   ```

---

## How to Run Directly via Kaggle Web UI (Method B: Browser)

1. Go to [kaggle.com/code](https://www.kaggle.com/code) and click **"New Notebook"**.
2. In the right-hand panel under **Notebook Settings**:
   - **Accelerator:** Select **GPU T4 x1** or **GPU T4 x2**.
   - **Internet:** Toggle **ON**.
3. Go to **File $\to$ Import Notebook** and upload [`kaggle/kaggle_fl_benchmark.ipynb`](file:///home/kriteshgoud/Documents/NMIMS/projects/CAPSTONE/kaggle/kaggle_fl_benchmark.ipynb).
4. Click **"Save Version" $\to$ "Save & Run All (Commit)"**.
5. You can now close your laptop! Kaggle will run all 200 simulations in the cloud and email you when the outputs are ready to download.
