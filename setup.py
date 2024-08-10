from distutils.core import setup

setup(
    name="cel",
    packages=["cel"],
    package_data={"cel": ["py.typed"]},
    version="0.1.0",
    description="",
    author="Ali Sorour Amini",
    author_email="ali.sorouramini@gmail.com",
    url="https://github.com/alisoam/cel-py",
    install_requires=["lark~=1.1.9"],
)
