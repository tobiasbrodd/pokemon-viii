# pokemon-swsh

A Pokemon Sword &amp; Shield Team Generator

## Download

Scrapes Galarian Pokedex Pokemon from Serebii.

```shell
> python3 download.py [options]
```

options:  
**-h, --help:**         Prints help message.  

## Images

Scrapes Galarian Pokedex images from Serebii.

```shell
> python3 images.py [options]
```

options:  
**-h, --help:**         Prints help message.  

## Team

Generates a Pokemon team.

```shell
> python3 team.py [options]
```

options:  
**-h, --help:**         Prints help message.  
**--size s:**           Sets size of the team to 's'. Default: '6'.  
**--team t:**           Sets team to 't'. Default: 'Empty'.
**--hp h:**             Sets minimum HP to 'h'. Default: '0'.  
**--attack a:**         Sets minimum attack to 'a'. Default: '0'.  
**--defense d:**        Sets minimum defense to 'd'. Default: '0'.  
**--spattack s:**       Sets minimum sp. attack to 's'. Default: '0'.  
**--spdefense s:**      Sets minimum sp. defense to 's'. Default: '0'.  
**--speed s:**          Sets minimum speed to 's'. Default: '0'.  
**--total t:**          Sets minimum total to 't'. Default: '0'.
**--weights w:**        Sets weights to 'w'. Default: '1,1,1,1,1,1'.  
**--types t:**          Sets types to 't. Default: 'All'.  
**--stage s:**          Sets stage to 'ws'. Default: 'None'.  
**--final:**            Only allow final evolutions.  
**--legendary:**        Don't allow legendary Pokemon.  
**--mytical:**          Don't allow mythical Pokemon.  
**--random:**           Randomize team generation.  
**--utypes:**           Enables unique type generation (if not random).
**--uteam:**            Enables unique team generation.
**--color:**            Enables colored output.
