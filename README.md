# python.copier

My personal [Copier](https://github.com/copier-org/copier) template
for Python projects managed by [PDM](https://github.com/pdm-project/pdm).

This copier template is mainly for my own usage,
but feel free to try it out, or fork it!

## Getting started

### Requirements

This project use [Copier](https://github.com/copier-org/copier) with [`copier-template-extensions`](https://github.com/copier-org/copier-templates-extensions)

You need to ensure they are installed before using this template, either with `pip`:

```shell
pip install copier copier-templates-extensions
```

or with [`pipx`](https://pypa.github.io/pipx/):

```shell
pipx install copier
pipx inject copier copier-templates-extensions
```

It also assume the following tools are installed:

- [pdm](https://pdm.fming.dev), optionnaly with [pdm-ide](https://github.com/noirbizarre/pdm-ide)
- [pre-commit](https://pre-commit.com)

If you don have them, you can also install them with [`pipx`](https://pypa.github.io/pipx/)

```shell
pipx install pdm
pipx inject pdm pdm-ide
```

```shell
pipx install pre-commit
```

### Applying template

Now that you are all set, you can just apply the template like any other Copier template:

```shell
copier "https://github.com/noirbizarre/python.copier.git" <project_name>
```

Or even shorter:

```shell
copier "gh:noirbizarre/python.copier" <project_name>
```

## Inspirations

This temlpate was inspaired by others so feel free to take a look at them:

- [pawamoy/copier-pdm](https://github.com/pawamoy/copier-pdm)
- [pdm-project/copier-pdm](https://github.com/pdm-project/copier-pdm)
