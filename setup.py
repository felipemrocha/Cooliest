from setuptools import setup

setup(
    name="TeamCooliest",
    version="0.0.0",
    packages=["src", "src.model", "src.GUI"],
    entry_points={
        "console_scripts": [
            "tc-model = src.model.calculate_chip_temp:main",
            "tc-gui = src.GUI.app:main",
            "tc-gui2 = src.GUI.fan_plot:main",
        ]
    },
)
