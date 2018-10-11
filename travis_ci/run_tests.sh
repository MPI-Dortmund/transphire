function find_files {
    file_names=$(find . -name '*.py' | grep --invert-match 'test')
    echo ${file_names}
}

function my_mypy {
    echo
    echo "##############"
    echo "MYPY"
    echo "##############"
    echo
    file_names=($(find_files))
    error=false
    for name in "${file_names[@]}"
    do
        echo ${name}
        mypy ${name} --disallow-untyped-defs --check-untyped-defs --disallow-incomplete-defs
        if [[ ${?} != 0 ]]
        then
            error=true
        fi
    done
    if [[ ${error} = true ]]
    then
        return 1
    else
        return 0
    fi
}


function my_pyflakes {
    echo
    echo "##############"
    echo "PYFLAKES"
    echo "##############"
    echo
    file_names=($(find_files))
    error=false
    for name in "${file_names[@]}"
    do
        echo ${name}
        pyflakes ${name}
        if [[ ${?} != 0 ]]
        then
            error=true
        fi
    done
    if [[ ${error} = true ]]
    then
        return 1
    else
        return 0
    fi
}

function my_pylint {
    echo
    echo "##############"
    echo "PYLINT"
    echo "##############"
    echo
    file_names=($(find_files))
    error=false
    for name in "${file_names[@]}"
    do
        echo ${name}
        pylint ${name} --rcfile=travis_ci/pylint.rc
        if [[ ${?} != 0 ]]
        then
            error=true
        fi
    done
    if [[ ${error} = true ]]
    then
        return 1
    else
        return 0
    fi
}

function my_pytest {
    echo
    echo "##############"
    echo "PYTEST"
    echo "##############"
    echo
    rm -r OUTPUT_TEST_FOLDER
    pytest --cov=transphire_transform --cov-report term-missing -s
    return ${?}
}

if [[ -z ${1} ]]
then
    names=('pytest' 'mypy' 'pylint' 'pyflakes')
    for name in "${names[@]}"
    do
        my_${name}
    done
else
        my_${1}
        exit ${?}
fi
