# ScryptCalc - Portable calculator for Scrypt KDF application with UI written in Python 3.7

ScryptCalc is a PyQt 5 UI frontend that uses hashlib's scrypt implementation. Some attempts have been made to clear secret info from the application's memory as soon as they're no longer needed there as well as on application close, but with Python being unmanaged and Qt as well underlying variable management implementations not being set in stone, no guarantees can be given.

The UI provides the ability to set Scrypt's N^2, P, and R parameters, as well as the output length in bytes and the output format.

Password, salt, and output size of max 192 are supported. The output can be formatted as one of the following: bin, hex, base32, base64, and base85.

When it comes to the Scrypt parameter N, the UI setting represents the exponent of the actual number of rounds, by the formula N = exp^2. So for example, setting an exponent of 10 will translate into a Scrypt N = 1024. This allows for using smaller numbers in the UI that need to be increased by less in order to keep up with the computational increase.

The memory estimate for computation based on the selected parameters is displayed in the UI.

It is also possible to clear the password field as soon as computation begins if the option is checked.

In addition, a file named "config.txt" can be placed in the application folder containing saved parameters in this example format:

```
nexp=10
r=8
p=2
length=30
salt=myUniqueSalt3056740568309530
format=hex
clear=1
```

The values provided will be automatically populated in the UI on application start. Clear can take 1/true/yes or 0/false/no as values.
