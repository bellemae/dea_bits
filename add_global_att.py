import click
import h5py
import netCDF4
import numpy
import xarray
import yaml
from datacube.storage.netcdf_writer import append_netcdf


def multiple_add_att(target_list, name, value):
    with open(target_list) as fl:
        file_list = [l for l in fl]

    while file_list:
        target = file_list.pop().strip()

        print(target + '...', end='')
        add_att(target, name, value)
        print('!')

        with open(target_list, 'wt') as fl:
            for l in file_list:
                fl.write(l)


def add_att(target, name, value):
    print(f"updating... {name}: {value}")
    nco = append_netcdf(target)
    setattr(nco, name, value)
    nco.close()

def new_att():
    name = 'source'
    value = 'Water Observation from Space Detection Algorithm v1.5'
    return name, value


@click.command()
@click.option('--target', type=click.Path())
@click.option('--target-list', type=click.Path())
def main(target, target_list):
    if target is not None and target_list is not None:
        raise ValueError('cannot do both')

    name, value = new_att()
    if target is not None:
        add_att(target, name, value)
    elif target_list is not None:
        multiple_add_att(target_list, name, value)
    else:
        raise ValueError('nothing to do')


if __name__ == '__main__':
    main()

