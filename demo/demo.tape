Output: turboprivate-demo.gif
FontFamily: "Cascadia Code", "JetBrains Mono", "Consolas"
FontSize: 14
Width: 900
Height: 540
Theme: Dracula
TypingSpeed: 50ms

Show "     TurboPrivate AI  v0.1.0  —  Self-Hosted LLM + Safety Governance"
Sleep 1s

Type "turbo doctor"
Sleep 300ms
Enter
Sleep 4s

Type "clear"
Sleep 200ms
Enter
Type "turbo --help"
Sleep 300ms
Enter
Sleep 3s

Type "turbo model --help"
Sleep 200ms
Enter
Sleep 2s

Type "clear"
Sleep 200ms
Enter
Type "turbo safety --help"
Sleep 200ms
Enter
Sleep 2s

Type "turbo model pull meta-llama/Llama-3-8B"
Sleep 200ms
Enter
Sleep 2s

Type "turbo model quantize meta-llama/Llama-3-8B --bits 4"
Sleep 200ms
Enter
Sleep 2s

Type "clear"
Sleep 200ms
Enter
Type "turbo safety check"
Sleep 200ms
Enter
Sleep 2s

Type "turbo infra init --name my-cluster"
Sleep 200ms
Enter
Sleep 2s

Type "turbo backup --name pre-deploy"
Sleep 200ms
Enter
Sleep 2s

Type "clear"
Sleep 200ms
Enter
Type "turbo doctor"
Sleep 300ms
Enter
Sleep 3s

Type "echo '=== TurboPrivate AI deployed! Visit http://localhost:8000/docs ==='"
Sleep 200ms
Enter
Sleep 2s
