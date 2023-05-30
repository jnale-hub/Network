document.addEventListener("DOMContentLoaded", () => {
    
    document.querySelectorAll(".like").forEach(likeButton => {
        likeButton.onclick = () => toggleLike(likeButton);
    })

    document.querySelectorAll(".edit").forEach(editButton => {
        editButton.onclick = () => {
            const postId = editButton.dataset.postId;
            const contentField = document.querySelector(`#content_${postId}`);
            const editForm = document.createElement("div");
            const saveButton = document.createElement("a");
            saveButton.innerHTML = 
            `<button form="edit-post${postId}" type="submit" class="btn btn-primary rounded-pill px-3 py-1 my-2">Save</button>`
            editForm.innerHTML =
            `<form id="edit-post${postId}">
            <textarea class="form-control" rows="3" required id="edit-post" name="content">${contentField.innerText}</textarea>
            </form>`
            const editField = editForm.querySelector("#edit-post");
            editButton.replaceWith(saveButton);
            contentField.replaceWith(editForm); 
            editField.focus();
            editField.setSelectionRange(editField.value.trim().length, editField.value.trim().length);
            editForm.querySelector("form").onsubmit = () => {
                const newContent = editField.value.trim();
                fetch(`/post/${postId}`, {
                    method: "PUT",
                    body: JSON.stringify({
                        "content": newContent
                    })
                })
                .then(() => {
                    contentField.innerHTML = newContent;
                    editForm.replaceWith(contentField);
                    saveButton.replaceWith(editButton);
                })
             }
        }
    })
})

function toggleLike(likeButton) {
    const postId = likeButton.dataset.postId;
    fetch(`/post/${postId}`, {
        method: "PUT",
        body: JSON.stringify({
            toggle_like: true
        })
    })

    .then(response => response.json())
    .then(result => {
        const oldNumLikes = parseInt(document.querySelector(`#num-likes-${postId}`).innerHTML);
        const newNumLikes = parseInt(result.num_likes);
        const span = likeButton.querySelector("span");
        document.querySelector(`#num-likes-${postId}`).innerHTML = newNumLikes;
        newNumLikes > oldNumLikes ? span.innerHTML = "Unlike": span.innerHTML = "Like";
    })
}

