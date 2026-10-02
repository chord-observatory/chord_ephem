<!-- Title: <type>(<scope>): <subject>, e.g. "feat(io): add LoadCorrDataFiles".
     It becomes the commit message on main and the release notes entry. -->

### What and why

<!-- What does this change, and why? Link the issue it addresses (Closes #...). -->

### How it was tested

<!-- Tests added, and anything checked by hand (data, configs, cluster runs). -->

### Checklist

- [ ] Tests added or updated, and `python -m pytest` passes
- [ ] Public code documented (NumPy docstrings) and docs updated
- [ ] `ruff format` and `ruff check` are clean
- [ ] Breaking changes (APIs, configs, file formats, dependencies) are described
      above and marked in the title with `!`
- [ ] No data files, notebook outputs or credentials committed
