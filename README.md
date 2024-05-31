# ScryptCalc - Portable calculator for Scrypt KDF application with UI written in Python 3.7

ScryptCalc is a PyQt 5 UI frontend that uses hashlib's Scrypt implementation.

Attempts have been made to clear secret info from the application's memory as soon as it's no longer needed there, but with Python being unmanaged and Qt as well underlying variable management implementations not being set in stone this only mitigates the amount of occurrences. Memory dumps will contain at least some recent inputs and their resulting passwords, usually 1-3 occurrences each. This is almost exclusively due to the mannerisms with string manipulation in Qt5's backend

The UI provides the ability to set Scrypt's N^2, P, and R parameters, as well as the output length in bytes and the output format.

Password, salt, and output size of max 192 are supported. The output can be formatted as one of the following: bin, hex, base32, base64, and base85.

When it comes to the Scrypt parameter N, the UI setting represents the exponent of the actual number of rounds, as per the formula N = exp^2. So for example, setting an exponent of 10 will translate into a Scrypt N = 1024.

The memory estimate for computation based on the selected parameters is displayed in the UI. Parameters are adjustable to any values that keep Scrypt's memory usage under 2GB. The limitations on how big the Scrypt parameters can get is dictated by hashlib's implementation.

Pressing ENTER in the input field will perform a computation. A finished computation will then auto-focus the "Copy result" button for convenience, so a sequence of typing the input, hitting ENTER, and following up with SPACEBAR after completion is enough to derive a password and fetch the result.

It is also possible to clear the password field as soon as computation begins if the option is checked.

The application will flash the taskbar when it is done computing, so it can be tabbed away from or minimized while waiting for the result.

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
