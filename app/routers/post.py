from fastapi import FastAPI, Response, HTTPException, status, Depends, APIRouter
from sqlalchemy import func
from .. import models, schemas, utils, oauth2
from sqlalchemy.orm import Session


from ..database import get_db
from typing import Optional, List


router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)


# get all


@router.get("/", response_model=List[schemas.PostOut])
# @router.get("/")
def get_posts(db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user), limit=5,
              search: Optional[str] = ""):
    # cursor.execute("""SELECT * FROM posts""")
    # posts = cursor.fetchall()
    print(limit)
    posts = db.query(models.Post).filter(
        models.Post.title.contains(search)).limit(limit).all()

    results = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).all()

    return results


# create one
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                (post.title, post.content, post.published))
    # new_post = cursor.fetchone()

    # conn.commit()
    print(current_user)

    new_post = models.Post(owner_id=current_user.id, ** post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post


# get one of any user (any login)


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # cursor.execute(""" SELECT * from posts WHERE id= %s """, (id))
    # post = cursor.fetchone()
    # post = db.query(models.Post, func.count(models.Vote.post_id)
    #                 ).filter(models.Post.id == id).first()

    post = db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} ws not found")

    return post

# delete post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # cursor.execute(""" DELETE FROM posts WHERE id=%s RETURNING *""", (id))
    # deleted_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id:{id} does not exixst")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    post_query .delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


# update a post
@router.put("/{id}", response_model=schemas.Post)
def updated_post(id, updated_post: schemas.PostCreate, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    # cursor.execute(""" UPDATE posts SET title = %s,content=%s,published=%s WHERE id=%s RETURNING *""",
    #                (post.title, post.content, post.published, id))
    # updated_post = cursor.fetchone()
    # conn.commit()
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exixst")
    post_query.update(updated_post.dict(), synchronize_session=False)

    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorized to perform requested action")

    db.commit()

    return post_query.first()
