from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

setup(
    name="ops_dashboard",
    version="0.0.1",
    description="Justyol Ops Dashboard — mobile-first operations PWA on ERPNext",
    author="Justyol",
    author_email="info@justyol.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires,
)
