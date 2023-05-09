from setuptools import setup

setup(
    name='plot_addresses',
    version='0.5',
    packages=['plot_addresses'],
    url='https://github.com/cookster9/neighborhood-plotter',
    license='MIT',
    author='andrewcook',
    author_email='acook999@gmail.com',
    description='Create a folium map of nashville home sales (data not included)',
    install_requires=['folium']
)
