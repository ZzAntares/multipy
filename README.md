# multipy

Clúster de procesamiento paralelo basado en un gestor de colas de tareas
asíncronas.

La idea principal de este proyecto es que sea sencillo extender una red de nodos
con `multipy` instalado a la cual se le puedan enviar funciones en código python
que serán ejecutadas paralelamente por el clúster, de manera que se pueda
utilizar la capacidad de procesamiento del clúster para reducir el tiempo de
cómputo que toma una tarea.

La manera en la que se planea utilizar `multipy` es la siguiente:

## Para ejecutar código en el cluster

```sh
$ multipy run micodigo.py
```

El programa leerá la función `main()` que deberá estar definida en tu programa y
la ejecutará en el clúster, los argumentos extras de la linea de comandos serán
pasados a la función `main`.

## Para extender el cluster con nuevos nodos

Por otro lado para extender el clúster bastará con ejecutar `multipy` de la
siguiente manera:

```sh
$ multipy node --host 10.0.0.10 --port 3000
```

El nodo se conectará al gestor del clúster que está ejecutándose en esa
dirección, a partir de ahí el nodo podrá recibir tareas para procesar.

## Para iniciar un gestor para un nuevo cluster

Para iniciar un clúster, uno de los nodos deberá actuar como un gestor de
tareas, se podría decir que éste gestor es el nodo maestro que recibe las tareas
a procesar y las distribuye entre todos los nodos registrados en el clúster.

Para iniciar el gestor utilice el comando

```sh
$ multipy manager --host 10.0.0.10 --port 3000
```

Esto inicia un servidor en la dirección y puerto especificados al cual otros
nuevos nodos pueden conectarse.
