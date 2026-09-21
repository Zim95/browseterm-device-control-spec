'''
This build file executes when hitting poetry install locally.
But when importing this package from git, this file is not run.

So, we need to manually run this file, generate the proto files and commit to git from now on.
'''

# builtins
import os
import pathlib
import glob


# constants
PACKAGE_DIR: str = "device_control_spec/"
PROTO_PATH: str = "spec/"
PACKAGE_NAME: str = "device_control_spec"


SPEC_BUILD_COMMAND: str = (
    f"python -m grpc_tools.protoc"
    f" --proto_path={PROTO_PATH} "
    f" --python_out={PACKAGE_DIR} "
    f" --grpc_python_out={PACKAGE_DIR} "
    f"{PROTO_PATH}*.proto"
)


def execute_command(command: str) -> None:
    """
    Execute the linux command.
    """
    try:
        os.system(command)
    except Exception as e:
        print(e)


def replace_import() -> None:
    """
    All imports will be made in device_control_pb2.py and device_control_pb2_grpc.py
    Find _pb2 imports, add PACKAGE_NAME.*_pb2 in the imports.
    """
    file_paths: map = map(lambda x: pathlib.Path(x),
                     glob.glob(f'{PACKAGE_DIR}device_control_*.py', recursive=True))
    type_modules: list = [
        "device_control_types_pb2",
        # Unlike container-maker-spec's service.proto (which defines no messages of its own -
        # every RPC signature type comes from types.proto), device_control.proto DEFINES
        # DeviceToCloud/CloudToDevice itself, so device_control_pb2_grpc.py imports
        # device_control_pb2 (its own sibling module) too - that self-import needs namespacing
        # exactly like the types import does, or it fails once installed as a package.
        "device_control_pb2",
    ]
    for file in file_paths:
        text: str = file.read_text()
        for type_module in type_modules:
            text = text.replace(f'\nimport {type_module}',
                                f'\nimport {PACKAGE_NAME}.{type_module}')
        file.write_text(text)


def build() -> None:
    """
    > Execute the command
    > Replace the import
    """
    execute_command(SPEC_BUILD_COMMAND)
    replace_import()


if __name__ == "__main__":
    build()
