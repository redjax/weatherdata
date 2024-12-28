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

Once you have installed the project (read the [setup instructions](#setup)), you can run different entrypoints with `uv run`. For example, to launch the [`weather_cli` app](./applications/cli/), you can run:

```shell
uv run python -m weather_cli
```

Or to see the [sandbox demo](./sandbox/demo/demo.py), you can just run:

```shell
uv run sandbox/demo/demo.py
```

You can omit `python` in your `uv run` commands; `uv` knows what you're trying to do when you run a `.py` file 😉 The exception to this rule is when running packages as a module, as you would with `python -m`. You still need to add that to your `uv` command.

### Using the monorepo

Developing in a monorepo is different from developing in other "flatter" repositories. In a regular repository, you might only have 1 service or application defined in your code. In a monorepo, you can define many services/applications and shared dependencies. You can bring various parts of the application together by installing modules in other modules (like the [`depends` package](./packages/depends/pyproject.toml), which import its settings in the `[tool.uv.sources]` section from the `settings` module: settings = { workspace = true }), import from other areas of the monorepo, and share code more easily between different applications and services.

Each type of repository has its purpose and place; I am choosing to structure this project as a monorepo so I can learn how to manage and work with them. Neither is better than the other, a good developer will choose when a monorepository format is right for their project.

### Adding packages

To add new packages to the app, create a path in [`packages/`](./packages) and initialize it with `uv init --package`. Note that if you're using VSCode and want type completion to work, you also need to edit the [`settings.json` file in the `.vscode/` directory](./.vscode/settings.json), adding the path to `"python.analysis.extraPaths": []`.

For example, to add a package named `nb_functions`, you might run the following commands:

```shell
## Create the directory where the package will live
mkdir -pv ./packages/notebook-functions
cd ./packages/notebook-functions

## Create the src directory & __init__.py/main.py files
mkdir -pv ./src/nb_functions
touch ./src/nb_functions/{__init__,main}.py

## Initialize the uv package
uv init --package

## Add code from another module in this repository, i.e. http-lib
uv add http-lib
```

Note that the source code name (`nb_functions`) differs from the parent path name (`notebook-functions`). You need to modify the new `pyproject.toml` file that was created when you ran `uv init --package`.

When a package's name differs from the parent directory like this, you will see an error like this when you try to add packages, build, or run anything with `uv`:

```
ValueError: Unable to determine which files to ship inside the wheel using the following heuristics: https://hatch.pypa.io/latest/plugins/builder/wheel/#default-file-selection

The most likely cause of this is that there is no directory that matches the name of your project (notebook-functions).

At least one file selection option must be defined in the `tool.hatch.build.targets.wheel` table, see: https://hatch.pypa.io/latest/config/build/

As an example, if you intend to ship a directory named `foo` that resides within a `src` directory located at the root of your project, you can define the following:

[tool.hatch.build.targets.wheel]
packages = ["src/foo"]
```

The fix for this is details in that last part of the error message. We need to add a section like the following to tell `uv` where the code it needs to build for this package lives:

```toml
## packages/notebook-functions/src/nb_functions/pyproject.toml

...

[tool.hatch.build.targets.wheel]
packages = ["src/nb_functions"]

...

```

This fixes the build error. Remember this when you are naming package and application parent directories.

Finally, if you're using VSCode, add the new path to your `settings.json` file:

```json
{
    ...,
    "python.analysis.extraPaths": [
        ...,
        "./packages/notebook-functions/src",
    ]
}
```

### Adding applications

[Applications](./applications/) import from [`packages/`](./packages/) and other areas of the repository, joining different parts of the code into functional apps meant to be built, distributed, and used.

For example, the [`weather_cli` application](./applications/cli) exposes a CLI written in [`cyclopts`](cyclopts.readthedocs.io/) that a user can run to call different parts of the code, like requesting the current weather.

Building an application is pretty much the same as [a package](#adding-packages). The main difference is when you initialize it, you run:

```shell
uv init --application --package
```

## The 'sandbox'

The [`sandbox/`](./sandbox/) path is a place where I can prototype or test small portions of the repository. The [demo](./sandbox/demo/) application is a constantly evolving file I use put together pre-packaged function calls by importing code from applications, packages, etc, and writing scripts like I might if I were to install these packages outside of this repository.

Sandbox code is just that; it is not packaged, it's not meant to be distributed, and scripts may come and go (I often delete things in the sandbox once I've integrated the code into the app somewhere else).

## Notes

## Links

- [Astral `uv`](https://docs.astral.sh/uv)
- [WeatherAPI docs](https://www.weatherapi.com/docs/)
  - [WeatherAPI interactive API explorer](https://www.weatherapi.com/api-explorer.aspx)
