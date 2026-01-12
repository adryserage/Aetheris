# Troubleshooting

## Common Errors

### API Key Not Defined
```
❌ Variable d'environnement [API_KEY] non définie
```

**Solution**: Create `.env` file with your API key:
```env
# For Gemini
GEMINI_API_KEY=your_key_here

# For OpenAI
OPENAI_API_KEY=your_key_here

# For Claude
ANTHROPIC_API_KEY=your_key_here
```

Or set environment variable:
```bash
# Linux/macOS
export GEMINI_API_KEY=your_key_here

# Windows PowerShell
$env:GEMINI_API_KEY='your_key_here'
```

### ModuleNotFoundError
```
ModuleNotFoundError: No module named 'xxx'
```

**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

Or reinstall:
```bash
pip install --force-reinstall adryserage-aetheris
```

### Claude Code Not Found
```
❌ Claude Code n'est pas installé ou introuvable
```

**Solution**: Install Claude Code:
```bash
npm install -g @anthropic-ai/claude-code
```

Verify:
```bash
aetheris fix --test
```

### GitHub CLI Not Authenticated
```
❌ gh CLI n'est pas disponible ou non authentifié
```

**Solution**:
```bash
# Install gh
brew install gh        # macOS
sudo apt install gh    # Ubuntu
winget install gh      # Windows

# Authenticate
gh auth login
```

### Slow Analysis
**Solutions**:
1. Reduce batch size:
   ```env
   BATCH_SIZE=5
   ```
2. Increase timeout:
   ```env
   TIMEOUT_SECONDS=120
   ```
3. Use faster model:
   ```env
   AI_MODEL=gemini-1.5-flash
   ```
4. Enable caching:
   ```env
   ENABLE_CACHE=true
   ```

### Logs Not Appearing
**Solution**: Check terminal UTF-8 support.

Windows:
```powershell
chcp 65001
```

### API Rate Limits
```
Rate limit exceeded
```

**Solutions**:
1. Wait and retry (automatic with backoff)
2. Reduce `BATCH_SIZE`
3. Enable `ENABLE_CACHE=true`
4. Use Batch API: `ENABLE_BATCH_MODE=true`

### Invalid API Key
```
❌ Erreur de validation de la clé API
```

**Solutions**:
1. Verify key is correct (no extra spaces)
2. Check API key permissions
3. Ensure billing is enabled (for paid models)
4. Try generating a new key

### Large Files Timeout
```
Timeout after 60 seconds
```

**Solution**: Increase timeout:
```env
TIMEOUT_SECONDS=180
```

## Debug Mode

Enable verbose logging:
```env
SHOW_REASONING=true
```

For Gemini thinking:
```env
ENABLE_THINKING=true
THINKING_BUDGET=2048
```

## Agent Selection Issues (v2.10)

### Unknown Agent Error
```
❌ Unknown agent: performance_agent
```

**Solution**: Use correct agent names:
```bash
# Core agents
aetheris analysis --agents code_analysis,architecture,security,metrics,vulnerability,qa

# Extended agents (v2.10)
aetheris analysis --agents type_safety,performance,api_contract,data_privacy
```

### Compliance Framework Not Found
```
❌ Unknown compliance framework: gdpr2
```

**Solution**: Use valid framework names:
```bash
aetheris analysis --compliance gdpr,hipaa,pci_dss,ccpa
```

### Extended Agent Not Running
Extended agents require the corresponding enable flags:
```env
ENABLE_TYPE_ANALYSIS=true
ENABLE_PERFORMANCE_ANALYSIS=true
ENABLE_API_CONTRACT_ANALYSIS=true
ENABLE_PRIVACY_ANALYSIS=true
```

## Cache Issues

### Force Re-analysis
```bash
ENABLE_CACHE=false aetheris analysis
```

### Clear Cache
```bash
rm -rf .cache/aetheris/
```

## PR Review Issues

### Can't Fetch PR
Check permissions:
```bash
gh auth status
gh api repos/owner/repo/pulls/123
```

### Comments Not Posting
1. Check `--dry-run` is not set
2. Verify write permissions on repo
3. Check if PR is open (not merged/closed)

## Fix Command Issues

### Parallel Mode Failures
Reduce batch size:
```bash
aetheris fix --auto --batch-size 5
```

### Retry Failed Bugs
```bash
aetheris fix --retry-failed
```

## Network Issues

### Connection Timeout
```
Connection timed out
```

**Solutions**:
1. Check internet connectivity
2. Verify firewall/proxy settings
3. Try a different network
4. Increase timeout: `TIMEOUT_SECONDS=180`

### SSL Certificate Errors
```
SSL: CERTIFICATE_VERIFY_FAILED
```

**Solutions**:
1. Update Python certificates:
   ```bash
   pip install --upgrade certifi
   ```
2. On macOS, run:
   ```bash
   /Applications/Python\ 3.x/Install\ Certificates.command
   ```

## Memory Issues

### Out of Memory
```
MemoryError
```

**Solutions**:
1. Reduce batch size: `BATCH_SIZE=3`
2. Analyze smaller subsets with `--files`
3. Close other applications
4. Increase system swap/virtual memory

## Platform-Specific

### Windows Path Issues
```
FileNotFoundError: [WinError 3]
```

**Solution**: Use forward slashes or raw strings:
```bash
aetheris analysis --files src/file1.py,src/file2.py
```

### macOS Gatekeeper
```
"aetheris" cannot be opened because the developer cannot be verified
```

**Solution**: Allow in System Preferences > Security & Privacy

### Linux Permission Denied
```
PermissionError: [Errno 13]
```

**Solution**:
```bash
chmod +x ~/.local/bin/aetheris
```

## Diagnostic Commands

```bash
# Check installation
aetheris --version

# Verify Python version
python --version

# Test API connectivity
curl -I https://generativelanguage.googleapis.com

# Check environment
env | grep -E "(API_KEY|AI_)"
```

## Getting Help

1. Check this documentation
2. Run with `--help`:
   ```bash
   aetheris --help
   aetheris <command> --help
   ```
3. Search [existing issues](https://github.com/adryserage/aetheris/issues)
4. Open a new issue on [GitHub](https://github.com/adryserage/aetheris/issues/new)

When reporting issues, please include:
- Aetheris version (`aetheris --version`)
- Python version (`python --version`)
- Operating system
- Error message (full traceback if available)
- Steps to reproduce
