# IF for some reason we have a dataset indexed into a datacube, but can't find the dataset yaml, this will create a simple one with information from datacube database.

import click
import datacube
dc = datacube.Datacube()
import yaml

# Get datasets which cover the provided region
def get_datasets(prod, x, y):

  query=({'x': x,
          'y': y,
          'crs':"EPSG:3577",})

  print("x:",x,", y:",y)
  return dc.find_datasets(product=prod, **query)


def prep_metadata(ds):

    meta = ds.metadata_doc

    for key in meta['image']['bands'].keys():
        meta['image']['bands'][key]['path'] = str(ds.local_path)

    return meta



@click.command(help="Prepare metadata for indexing into a datacube.")

@click.option('--x', required=True, type=(int, int))
@click.option('--y', required=True, type=(int, int))
@click.option('--product', required=True, type=str)
@click.option('--output', required=True, help="Write dataset docs into this path",
              type=click.Path(file_okay=False, exists=False, writable=True))


def main(x, y, product, output):
  print("Creating dataset yamls for "+product)

  datasets = get_datasets(product, x, y)

  for dataset in datasets:
    print(dataset)

    path = dataset.local_path
    out = path.name[0:-3] + ".yaml"
    meta = dataset.metadata

    with open(output + out, 'w') as stream:
        yaml.dump(prep_metadata(dataset), stream)


if __name__ == "__main__":
    main()





