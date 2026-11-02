catalog
    shop
        number     = external_dataset:shop_information
        book
            __NEW_DATASET__ = title_and_author title_and_genre
            id     = dataset:title_and_author dataset:title_and_genre
            author = dataset:title_and_author
            title  = dataset:title_and_author dataset:title_and_genre
            genre  = dataset:title_and_genre,name:style
            __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre
