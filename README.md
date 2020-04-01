# catwalk

`catwalk` is a model wrapping and serving platform.

This README contains technical information about the python package.
For User documentation, please refer to the [Wiki](https://github.com/LeapBeyond/catwalk/wiki/).

## Project overview

`catwalk` provides a simple and automated method to wrap a generic python-based model into a production-
ready, dockerised REST API server.
The project aims to automatically wrap a model via a CI/CD pipeline, or locally with a CLI, in a simple and flexible way
and with a single point of configuration.
This model image can then be integrated and deployed into cloud services.

Note that at the time of writing, CD into a cloud service is out-of-scope for `catwalk`.

### Folder structure

- `catwalk` - Contains the `catwalk` python module itself.
- `example_models` - Contains example models for testing and starting points users can use as a basis for their own model.
- `tests` - Contains the unit test suite for catwalk.
- `tutorials` - Contains code for various catwalk tutorials.

## Quick start

1. Perform setup steps (below).
2. Implement a `model.py` and `model.yml` following [the correct interface](https://github.com/LeapBeyond/catwalk/wiki/Models), or use one of the example models in `example_models`.
3. Test your model with `catwalk test-model` and `catwalk test-server`.
4. Serve your model with `catwalk serve --debug`.
5. (Optional) Build a model server image with `catwalk build-prep` and `catwalk build`.
6. (Optional) Test the built image with `catwalk test-image`.
7. (Optional) Deploy with `catwalk deploy-prep` and `docker-compose up`.

## Setup

This project uses [tox](https://tox.readthedocs.io/) to specify tests and environments.  

To develop the module, setup a venv and install it in "editable" mode.

This can be done with `tox`:

```bash
$ tox --devenv catwalk-venv
```

Or with `pip` in an existing venv:

```bash
(catwalk-venv) $ pip install --editable .
```

### Running the tests

The test suite can be simply run with `tox`:

```bash
$ tox
```

## License

Copyright 2020 Leap Beyond Analytics

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
