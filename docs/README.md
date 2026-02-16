# AI Room Scan â€” Project (Ahmed: integration & docs)

## Quick start (Ahmed: CPU-Optimized demo)

1. Clone repo:
   ```powershell
   git clone https://github.com/Ahmedimtiaz-github/Scan.git
   cd Scan
Create virtualenv (recommended):

python -m venv venv
.\venv\Scripts\Activate.ps1
pip install --upgrade pip
Install development/test deps (lightweight):

pip install -r requirements.txt
Run the Fast preset example (placeholder scaffolding):

powershell .\scripts\run_local.ps1 -InputPath "samples/example.jpg" -OutputDir "outputs"
Presets mapping
fast â€” minimal models & 512Ã—512, 20 steps (default for CPU)

balanced â€” medium quality & 768Ã—768, 25 steps

quality â€” high quality & slower (1024Ã—1024, 30â€“50 steps)

Acceptance criteria (Ahmed)
python -m src.main --mode image --preset fast --input <image> should produce:

outputs/frame_0001_styled.png (placeholder until Zohaib's module is integrated)

outputs/output_video_placeholder.txt
