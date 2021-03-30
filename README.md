# pokemon-swsh

A Pokemon Sword &amp; Shield Team Generator

## Team

Generates a Pokemon team and prints the team as ASCII images.

![Team in greyscale](https://github.com/tobiasbrodd/pokemon-swsh/blob/master/examples/team_grey.png)
![Team in color](https://github.com/tobiasbrodd/pokemon-swsh/blob/master/examples/team_color.png)

```shell
> python3 team.py [options]
```

options:  
**-h, --help:**         Prints help message.  
**--seed s:**           Sets random seed to 's'. Default: 'None'.  
**--dex d:**            Sets dex to 'd'. Default: 'ALL'.  
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
**--gen g:**            Sets team generator 'g'. Default: 'NAIVE'.  
**--weight w:**         Sets weight to 'w'. Default: '0.5'.  
**--gens g:**           Sets genetic generations to 'g'. Default: '10'.  
**--prop p:**           Sets genetic proportion to 'p'. Default: '0.8'.  
**--teams t:**          Sets genetic teams to 't'. Default: '100'.  
**--cross c:**          Sets genetic crossing to 'c'. Default: '2'.  
**--mut m:**            Sets genetic mutations to 'm'. Default: '3'.  
**--final:**            Only allow final evolutions.  
**--legendary:**        Don't allow legendary Pokemon.  
**--mytical:**          Don't allow mythical Pokemon.  
**--ultra:**            Don't allow ultra beast Pokemon.  
**--utypes:**           Enables unique type generation (only for NAIVE/RANDOM).  
**--uteam:**            Enables unique team generation (only for NAIVE/RANDOM).  
**--color:**            Enables colored output.  

## Download

Scrapes Galarian pokedex Pokemon from Serebii.

```shell
> python3 download.py [options]
```

options:  
**-h, --help:**         Prints help message.  
**--dex d:**            Sets dex to 'd'. Default: 'GALAR'.  

## Images

Scrapes Galarian pokedex images from Serebii.

```shell
> python3 images.py [options]
```

options:  
**-h, --help:**         Prints help message.  
**--dex d:**            Sets dex to 'd'. Default: 'GALAR'.  

## Generators

- NAIVE: Determines team members by first selecting best team types.
- RANDOM: Randomly selects team members.
- GENETIC: Selects team members by using a genetic algorithm.
