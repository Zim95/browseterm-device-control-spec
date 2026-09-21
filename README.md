# browseterm-device-control-spec
[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)

Protobuf API spec for the Browseterm Device Control gRPC stream: the single outbound,
bidirectional connection a Device Agent opens to Cloud (`DeviceControl.Connect`), used to deliver
durable lifecycle commands (Create/Delete/Hibernate/Resume/Reconcile) and report back status,
progress, and results. See `BROWSETERM_CLOUD_CONTROL_PLANE_MIGRATION.md` Part 5/6 for the full
design.

Device Agent always dials Cloud; Cloud never calls into a customer-controlled machine.

## Versioning

The proto `package` is `browseterm.device.control.v1`. Every message and enum in
`spec/device_control_types.proto` mirrors `browseterm-db`'s `device_commands` model
(`CommandOperation`/`CommandStatus`) - keep them in sync when either changes. Never reuse a field
number; add new fields/enum values instead. `Hello.protocol_version` lets Cloud reject an
incompatible/too-old Device Agent with a clear upgrade instruction rather than silently
misbehaving.

# How to Install locally:
- Clone the repository:
    ```bash
    $ git clone https://github.com/Zim95/browseterm-device-control-spec
    ```
    This will create a directory called `browseterm-device-control-spec` and clone the files
    within that directory.

    If you want a custom directory name:
    ```bash
    $ git clone https://github.com/Zim95/browseterm-device-control-spec <target-directory>
    ```

- Navigate to the target directory (`browseterm-device-control-spec` by default) and hit:
    ```bash
    $ poetry install
    ```
    This will run `build.py` and generate the protobuf files and also install it automatically in
    your virtual environment.

# How to make it installable from git:
- When installing from `git`, the `build.py` file is not run.

- In this case we need to run it manually and generate the protobuf files.

- First, create the virtual environment. So that it installs all required dependencies.
    ```bash
    $ poetry shell
    ```
    This creates the virtual environment. Now install the required dependencies.
    ```bash
    $ poetry install --no-root
    ```

- Now hit build.py
    ```bash
    $ python build.py
    ```
    This will generate the files.

- Next, commit these changes to git.

- If someone downloads them from git, then these protobuf files will also be copied to
  site-packages.

- You can now add this package to poetry using:
    ```bash
    $ poetry add git+https://github.com/Zim95/browseterm-device-control-spec.git@<tag>
    ```

# How to update tag:
- Update the version in `pyproject.toml`:

- Next, create the git tag:
    ```bash
    $ git tag <tagname> && git push -f origin <tagname>
    ```

- Overwrite the old tag:
    ```bash
    $ git tag -d <tagname> && git tag <tagname> && git push -f origin <tagname>
    ```
