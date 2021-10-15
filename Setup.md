# Setting up gem5 for the experiments

As some of the changes required by our experiments are not yet merged to the
mainline, you need to do the following to have access to all the code base
needed.

First, download the gem5 repo:

```console
$ git clone https://gem5.googlesource.com/public/gem5 && (cd gem5 && f=`git rev-parse --git-dir`/hooks/commit-msg ; mkdir -p $(dirname $f) ; curl -Lo $f https://gerrit-review.googlesource.com/tools/hooks/commit-msg ; chmod +x $f)
```

Now, checkout the develop branch:

```console
$ git checkout develop
```

Now, download all the changes to generators and components library as a branch (change 51613):

```console
$ git fetch https://gem5.googlesource.com/public/gem5 refs/changes/13/51613/1 && git checkout -b change-51613 FETCH_HEAD
```

Now, cherry-pick the change that adds multi-channel memory to the components library:

```console
$ git fetch https://gem5.googlesource.com/public/gem5 refs/changes/87/51287/4 && git cherry-pick FETCH_HEAD
```

# Running memory factory

Use the script "automate\_all.sh" to run experiments using DDR3, DDR4, LPDDR3,
and HBM. The number of channels vary from 1 to 16. Use the same file to change
such parameters.

```console
$ ./automate_all.sh <output_directory>
```

Output is redirected to:

```
<output_directory>/<memory_type>/<number_of_channels>/<current_date_and_time>
```
