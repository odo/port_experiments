# benchmarking [erlang ports](http://erlang.org/doc/reference_manual/ports.html)

this is a quick and dirty approach for a rough estimation.
much of the code was taken from [this howto](https://github.com/pkazmier/erlang-port-howto).

## Assumptions
* pool of running executables
* executables echo payload without performing any real computation

## Build and start

`git clone git://github.com/odo/port_experiments`

`make start`

## Usage

the one method to call is benchmark/4:

`benchmark(PoolSize, PayloadLength, Samples, Parallel)`

- PoolSize: nbumber of executables to start
- PayloadLength: number of Bytes in the payload going in a and out
- Samples: number of samples to take
- Parallel: number of clients accessing the executables

```erlang
1> echo:benchmark(10, 13 * 1024, 10000, 5).
{{10,13312,10000,5},7770.357949309293,103439005.0212053}
```

The return value is the arguments, the operations per second and bytes per second.

`exec: ./priv/echo.py: not found`?
check if your interpreter matches the one in `priv/echo.py`?

## Results

- Erlang/OTP 18
- python2.7
- FreeBSD 10
- 2 * Intel Xeon CPU E3-1230 v3 @ 3.30GHz = 8 cores
- 32 GB RAM

- 13 kB payload
- 100 clients
- 10000 samples
- what is a good number of executable?

```erlang
f(Res), Res = [ echo:benchmark(NoEx, 13 * 1024, 1000, 100) || NoEx <- lists:seq(1, 20)].
[{{1,13312,1000,100},2269.276940288516,30208614.629120726},
 {{2,13312,1000,100},4064.6110573679207,54108102.39568176},
 {{3,13312,1000,100},4764.967955590499,63431253.42482072},
 {{4,13312,1000,100},5076.760620583218,67581837.3812038},
 {{5,13312,1000,100},6203.127616944464,82576034.83676471},
 {{6,13312,1000,100},6331.518298087882,84285171.58414587},
 {{7,13312,1000,100},6760.822386435087,90000067.60822387},
 {{8,13312,1000,100},6613.581651279066,88039998.94182694},
 {{9,13312,1000,100},6760.182524928173,89991549.77184384},
 {{10,13312,1000,100},6468.723720809884,86111650.17142117},
 {{11,13312,1000,100},6175.2409887795875,82204808.04263386},
 {{12,13312,1000,100},6056.935190793459,80629921.25984251},
 {{13,13312,1000,100},6317.5583900334195,84099337.28812487},
 {{14,13312,1000,100},6422.3600888854635,85494457.50324328},
 {{15,13312,1000,100},7375.6647317839515,98184848.90950796},
 {{16,13312,1000,100},5650.643325742636,75221363.95228598},
 {{17,13312,1000,100},5663.091368316137,75387072.29502441},
 {{18,13312,1000,100},7331.324550406523,97594592.41501163},
 {{19,13312,1000,100},7545.973845654651,100452003.83335471},
 {{20,13312,1000,100},7005.057651624474,93251327.45842499}]
```

so it seems to max out at about 6760 ops (~90 MB/s) with 9 workers (~ number of CPUs), lets stay with 10 and see how payload impacts performance:

- 10 executables
- 100 clients
- 1000 samples
- variable payload

top says:

```
  PID USERNAME    THR PRI NICE   SIZE    RES STATE   C   TIME    WCPU COMMAND
51156 deploy       23  52    0  8797M  4427M uwait   1   7:23 731.45% beam.smp
55730 deploy        1  22    0 34336K  9056K piperd  0   0:00  32.67% python2.7
55739 deploy        1  22    0 34336K  9056K piperd  0   0:00  32.47% python2.7
55740 deploy        1  22    0 34336K  9056K piperd  5   0:00  32.37% python2.7
55735 deploy        1  22    0 34336K  9056K piperd  0   0:00  32.08% python2.7
55738 deploy        1  22    0 34336K  9056K piperd  4   0:00  31.88% python2.7
55741 deploy        1  22    0 34336K  9056K piperd  0   0:00  31.88% python2.7
55736 deploy        1  22    0 34336K  9056K pipewr  0   0:00  31.79% python2.7
55737 deploy        1  22    0 34336K  9056K piperd  5   0:00  31.79% python2.7
55742 deploy        1  22    0 34336K  9056K pipewr  0   0:00  31.59% python2.7
55733 deploy        1  22    0 34336K  9056K pipewr  0   0:00  31.49% python2.7
```

so as expected everyone is waiting for data from the pipe (in and out).


```erlang
f(Res), Res = [ echo:benchmark(10, PayloadLength * 1240 + 1, 1000, 100) || PayloadLength <- [0, 1, 5, 10, 20, 50, 100, 200, 500]].

[{{10,1,1000,100},48409.74003969599,48409.74003969599},
 {{10,1241,1000,100},22062.392445836827,27379429.025283504},
 {{10,6201,1000,100},8757.410959024075,54304705.356908284},
 {{10,12401,1000,100},6887.431814425037,85411041.9306849},
 {{10,24801,1000,100},3285.572067380512,81485472.84310408},
 {{10,62001,1000,100},1190.07524845796,73785855.47964197},
 {{10,124001,1000,100},555.9814991596339,68942261.87729377},
 {{10,248001,1000,100},200.17699650030556,49644095.30907228},
 {{10,620001,1000,100},82.72972348251763,51292511.288884416}]
 ```

 So we see there is an optimum at around 12 KB payload size with ~81 MB/s.
 
