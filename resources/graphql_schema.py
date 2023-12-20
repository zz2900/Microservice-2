import graphene

from dbconnector import get_db_conn

## use graphql to search book
class BookType(graphene.ObjectType):
    id = graphene.String()
    title = graphene.String()
    author = graphene.String()
    year = graphene.Int()
    details = graphene.String()

class Query(graphene.ObjectType):
    books = graphene.List(BookType, title=graphene.String())

    def resolve_books(self, info, title=None):
        conn = get_db_conn()
        query = "SELECT * FROM books"
        if title is not None:
            query += f" WHERE title like '%{title}%'"
        print("Parsed SQL from GraphQL: " + query)
        result = conn.execute(query).fetchdf()
        return [BookType(**row) for index, row in result.iterrows()]

schema = graphene.Schema(query=Query)

#