Output: turboprivate-demo.gif
FontSize: 16
Width: 900
Height: 600
TypingSpeed: 80ms

# Show the logo and doctor check
Type "turbo doctor"
Sleep 1s
Enter
Sleep 4s

# Clear and show CLI help
Type "clear"
Enter
Type "turbo --help"
Enter
Sleep 3s

# Show model commands
Type "turbo model --help"
Enter
Sleep 2s

# Show safety commands
Type "turbo safety --help"
Enter
Sleep 2s

# Show infra commands
Type "turbo infra --help"
Enter
Sleep 2s

# Pull a model
Type "clear"
Enter
Type "turbo model pull meta-llama/Llama-3-8B"
Enter
Sleep 2s

# Quantize it
Type "turbo model quantize meta-llama/Llama-3-8B --bits 4 --method awq"
Enter
Sleep 3s

# Serve it
Type "turbo model serve meta-llama/Llama-3-8B --replicas 2"
Enter
Sleep 2s

# Check safety
Type "turbo safety status"
Enter
Sleep 2s

# View audit
Type "turbo audit view --hours 48 --blocked-only"
Enter
Sleep 2s

# Create a backup
Type "turbo backup --name pre-deploy --encrypt"
Enter
Sleep 2s

# Generate infra config
Type "turbo infra init --provider bare-metal --name prod-cluster"
Enter
Sleep 2s

# Deploy
Type "turbo infra deploy --config turboprivate.yaml"
Enter
Sleep 3s

# Final status
Type "turbo doctor"
Enter
Sleep 3s

Type "echo '🚀 TurboPrivate AI deployed successfully!'"
Enter
Sleep 2s
