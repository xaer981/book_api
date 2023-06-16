from schemas import Message

NOT_FOUND_BOOK_ID = 'Book with id `{book_id}` doesn\'t exist.'
NOT_FOUND_CHAPTER_NUMBER = ('Requested chapter № {chapter_number} '
                            'doesn\'t exist in book № {book_id}.')
NOT_FOUND_AUTHOR_ID = 'Author with id `{author_id}` doesn\'t exist.'
RESPONSES = {
    404: {'model': Message,
          'description': 'Item not found'}
}
