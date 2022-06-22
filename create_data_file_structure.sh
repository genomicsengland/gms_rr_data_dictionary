#!/bin/bash
# script to refresh the data dictionary files and add in any new tables/columns
# ! doesn't check for things that have been removed
# requires single argument of directory to output structure to
mkdir -p $1
cd $1 || { echo 'unable to cd into target directory' ; exit 1; }

create_new_column () {
    # create a new template column yaml file in table's folder
    template_file="data_type: tbc\ndescription: tbc"
    echo -e $template_file > $1/$2.yaml
    echo "$1.$2 column created"
}

refresh_table () {
    # refresh a table's folder of files
    template_table_index="caption: tbc\ndescription: tbc"
    # if folder doesn't exist then create it with index.yaml
    if [ ! -d $1 ]
    then
        mkdir -p $1
        echo -e $template_table_index > $1/index.yaml
        echo "$1 table created"
    fi
    # get all the columns in that table and create column files if they don't exist
    psql -h localhost -p 5432 -U simon -F ' ' -Atc "select column_name from information_schema.columns where table_catalog = 'gms_research_release' and table_name = 'vw_$1'" gms_research_release |\
        while read col
        do
            if [ ! -f "$1/$col.yaml" ]
            then
                create_new_column $1 $col
            fi
        done
}

deprecate_table () {
    mv $1 $1_deprecated
    echo "$1 table deprecated"
    for i in `find $1_deprecated -type f -name "*.yaml"`
    do
        echo $i
        if [ ! $i = "$1_deprecated/index.yaml" ]
        then
            deprecate_column $i
        fi
    done
}

deprecate_column () {
    mv $1 ${1%.yaml}_deprecated.yaml
    echo "$1 column deprecated"
}

psql -h localhost -p 5432 -U simon -Atc "select distinct regexp_replace(table_name, '^vw_', '') from information_schema.columns where table_catalog = 'gms_research_release' and table_name not in ('vw_participant_list', 'vw_participant_cohort', 'vw_referral_list', 'vw_referral_cohort', 'vw_encryption_seed') and table_name like 'vw_%'" gms_research_release |\
while read tbl
do
    refresh_table $tbl
done
