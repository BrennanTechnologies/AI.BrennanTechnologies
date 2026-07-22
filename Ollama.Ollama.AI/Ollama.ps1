# Set environment variables for Ollama
$env:OLLAMA_LLM_LIBRARY = "cpu" # Use CPU for inference
$env:OLLAMA_GPU_DISABLED = "1" # Disable GPU usage

<#
I’ve confirmed the model runs when Ollama is forced onto the CPU backend,
and I’m updating the PowerShell script so it avoids the CUDA crash on future runs.

The error is caused by Ollama trying to use an incompatible GPU/CUDA path.
I verified that forcing the CPU backend works, and I updated the script to do that automatically.

 If you still want GPU support later, the next step is to update or reinstall the NVIDIA driver/CUDA stack that matches your current Ollama build.
#>

<#
I’m pulling the relevant Ollama and NVIDIA guidance together so I can give you the exact steps that match your setup.

The practical way to do it on your machine is:

Update the NVIDIA driver cleanly
Open the NVIDIA driver page and download the driver for your card: GeForce GTX 1080 Ti.
Install it using "Custom" → "Perform a clean installation".
Reboot the PC.
Verify the driver is active

Run `nvidia-smi` in the command prompt to check the driver version and GPU status.
nvidia-smi

You should see your GPU listed and the driver version.

Re-enable GPU in Ollama
In Ollama.ps1, remove or comment out:

$env:OLLAMA_LLM_LIBRARY = "cpu"
$env:OLLAMA_GPU_DISABLED = "1"

Then restart Ollama and test:
ollama serve
ollama run llama3.1 "Hello"


#>

# Kill any existing Ollama process and start a new one
Stop-Process -Name ollama -Force -ErrorAction SilentlyContinue
Start-Process -FilePath "ollama" -ArgumentList "serve" -WindowStyle Hidden
Start-Sleep -Seconds 3

#winget install Ollama.Ollama
#ollama pull llama3.1
#ollama pull codellama

# Run the model
ollama run llama3.1

Write-Host ""
Write-Host "Endpoints:"
Write-Host "http://localhost:11434/api/generate"
Write-Host "http://localhost:11434/api/embeddings"

Write-Host " Use it over HTTP -- The server is listening at: http://localhost:11434"
# curl http://localhost:11434/api/generate -d "{\"model\":\"llama3.1\",\"prompt\":\"Hello\"}"
