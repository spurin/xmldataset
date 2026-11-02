catalog
    shop
        number     = external_dataset:shop_information
        book
            id     = dataset:title_and_author dataset:title_and_genre
            author = dataset:title_and_author
            title  = dataset:title_and_author dataset:title_and_genre
            genre  = dataset:title_and_genre
            __EXTERNAL_VALUE__ = shop_information:number:title_and_author shop_information:number:title_and_genre
