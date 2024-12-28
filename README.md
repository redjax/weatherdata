# WeatherData Monorepo <!-- omit in toc -->

I use weather APIs frequently to help me learn programming things. I'm continuing that trend by learning to build a monorepo with Python and [`uv`](https://docs.astral.sh/uv).

## Table of Contents <!-- omit in toc -->

- [Requirements](#requirements)
- [Setup](#setup)
- [Usage](#usage)
  - [Using the monorepo](#using-the-monorepo)
  - [Adding packages](#adding-packages)
  - [Adding applications](#adding-applications)
- [The 'sandbox'](#the-sandbox)
- [Notes](#notes)
- [Links](#links)

## Requirements

- [`uv`](https://docs.astral.sh/uv): The packages (and the repository itself) are managed with `uv`.
  - If you haven't already tried it, you should!
  - `uv` can [even install Python for you](), meaning `uv` is the only dependency you need to install for this monorepo.
- (Optional) Python: If you want to install Python (or already have it installed), `uv` will use the system version of your Python.

## Setup

- Clone this repository
  - `git clone https://github.com/redjax/weatherdata`
- Create your configuration files
  - Copy the following files in [`config/`](./config):
    - General configurations:
      - `settings.toml` -> `settings.local.toml`
      - `.secrets.toml` -> `.secrets.local.toml`
    - Database configuration:
      - `database/settings.toml` -> `database/settings.local.toml`
      - `database/.secrets.toml` -> `database/.secrets.local.toml`
    - [weatherapi](https://www.weatherapi.com/) configuration:
      - **NOTE**: You need to sign up for a [free API key on WeatherAPI's site](https://www.weatherapi.com/signup.aspx).
      - `weatherapi/settings.toml` -> `weatherapi/settings.local.toml`
      - `weatherapi/.secrets.toml` -> `weatherapi/.secrets.local.toml`
- Run `uv sync` to install required packages
  - This repository uses [`uv` workspaces](https://docs.astral.sh/uv/concepts/projects/workspaces/) to build modules in [`applications/`](./applications) and [`packages`](./packages).
  - Each of the projects in these directories is a Python package with a `pyproject.toml` file, intialized with `uv init --package`.
  - When `uv` runs any part of this repository, it will build everything and then execute the command you ran.
  - If you want to manually build the project, you can run `uv build`

## Usage

...

### Using the monorepo

...

### Adding packages

...

### Adding applications

...

## The 'sandbox'

...

## Notes

...

## Links

- [Astral `uv`](https://docs.astral.sh/uv)
- [WeatherAPI docs](https://www.weatherapi.com/docs/)
  - [WeatherAPI interactive API explorer](https://www.weatherapi.com/api-explorer.aspx)
