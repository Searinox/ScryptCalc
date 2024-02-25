# ScryptCalc - Portable Scrypt KDF application

ScryptCalc is a PyQt 5 UI frontend that uses hashlib's scrypt implementation.

The UI provides the ability to set Scrypt's N^2, P, and R parameters, as well as the output length in bytes and the output format.

Supported output formats are: bin, hex, base32, base64, and base85.

When it comes to the Scrypt parameter N, the UI setting represents the exponent of the actual number of computations, by the formula N = exp^2. So for example, setting an exponent of 10 will translate into a Scrypt N = 1024. This allows for using smaller numbers in the UI that need to be increased by less in order to keep up with the computational increase.

In addition, a file named "config.txt" can be placed in the application folder containing saved parameters in this example format:

```
nexp=10
r=8
p=2
length=30
salt=myUniqueSalt3056740568309530
format=hex
```

The values provided will be automatically populated in the UI on application start.
