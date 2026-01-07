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

## Getting Help

1. Check this documentation
2. Run with `--help`:
   ```bash
   aetheris --help
   aetheris <command> --help
   ```
3. Open issue on [GitHub](https://github.com/adryserage/aetheris/issues)
