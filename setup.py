from setuptools import setup

setup(name="gym_pacman",
      version="0.1.0",
      install_requires=["gym", "numpy", "pygame"],
      packages=["gym_pacman", "gym_pacman.envs"],
      include_package_data=True
)
