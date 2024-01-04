# basic-foundation
Opinionated Foundation Boilerplate for a SaaS Platform

* Boring tech 
* Reproducible builds
* Development flow 
* 100% test coverage
* Easy to extend

## Assumptions

* Requires a python installation (recommend python [3.12](https://docs.python.org/release/3.12.1/whatsnew/3.12.html))
* Github access https://docs.github.com/en/get-started/quickstart/set-up-git
* IDE (.idea) file is included

## Getting started

### Install Hatch 

https://hatch.pypa.io/latest/install/

Using homebrew (OS X)
```bash
brew install hatch
```

Create a new project
```bash
 hatch new "basic-api" 
```

```
basic-api
├── src
│   └── basic_api
│       ├── __about__.py
│       └── __init__.py
├── tests
│   └── __init__.py
├── LICENSE.txt
├── README.md
└── pyproject.toml
```

cd basic-api

```bash
hatch env create
```

enter shell 
```bash
hatch shell
```
