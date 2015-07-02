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
{{10,13312,10000,5},53217.815195814954,708435555.8866887}
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
[{{1,13312,1000,100}, 15000.825045377496,199690983.00406522},
 {{2,13312,1000,100}, 20496.843486103142,272853980.487005},
 {{3,13312,1000,100}, 25366.546598346104,337679468.3171833},
 {{4,13312,1000,100}, 27126.00027126,    361101315.6110131},
 {{5,13312,1000,100}, 27899.450380827497,371397483.46957564},
 {{6,13312,1000,100}, 24541.684050359538,326698898.0783861},
 {{7,13312,1000,100}, 22465.85190510424, 299065420.5607476},
 {{8,13312,1000,100}, 19430.30350134069, 258656200.2098473},
 {{9,13312,1000,100}, 23129.944025535457,307905814.867928},
 {{10,13312,1000,100},19299.058205959547,256909062.8377335},
 {{11,13312,1000,100},20398.17232375979, 271540469.97389036},
 {{12,13312,1000,100},19801.9801980198,  263603960.39603958},
 {{13,13312,1000,100},17841.84984299172, 237510705.10990578},
 {{14,13312,1000,100},18253.504672897197,242990654.20560747},
 {{15,13312,1000,100},17320.816156857312,230574704.68008453},
 {{16,13312,1000,100},23150.291693675343,308176683.02620614},
 {{17,13312,1000,100},17031.422975389592,226722302.64838627},
 {{18,13312,1000,100},21585.68437412308, 287348630.38832647},
 {{19,13312,1000,100},13754.59059461095, 183101109.995461},
 {{20,13312,1000,100},17172.983462416927,228606755.85169414}]
```

so it seems to max out at about 23129 ops (~300 MB/s) with 9 workers (~ number of CPUs), lets stay with 10 and see how payload impacts performance:

- 10 executables
- 100 clients
- 1000 samples
- variable payload

```erlang
f(Res), Res = [ echo:benchmark(10, PayloadLength * 1240 + 1, 1000, 100) || PayloadLength <- [0, 1, 5, 10, 20, 50, 100, 200, 500]].

[{{10,1,1000,100},     24837.932490499494,24837.932490499494},
 {{10,1241,1000,100},  23617.770010155644,29309652.582603153},
 {{10,6201,1000,100},  21346.539725910432,132369892.84037058},
 {{10,12401,1000,100}, 24792.36395190281, 307450105.3675468},
 {{10,24801,1000,100}, 18201.674554058973,451419730.61521655},
 {{10,62001,1000,100}, 14088.674114879048,873511883.7966158},
 {{10,124001,1000,100},10358.400662937642,1284452040.6049306},
 {{10,248001,1000,100},5013.109280769212, 1243256114.7400453},
 {{10,620001,1000,100},1634.8497654808011,1013608489.4478621}]
 ```

 So we see there is an optimum at around 60 KB payload size with ~870 MB/s.
 
