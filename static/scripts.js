function handleThumbsUp(recipeId) {
    // Logic to handle thumbs up on a recipe
    console.log(`Recipe ${recipeId} thumbs up!`);
}

function handleComment(recipeId, comment) {
    // Logic to handle adding a comment to a recipe
    console.log(`Comment on recipe ${recipeId}: ${comment}`);
}

// Example usage
document.querySelectorAll('.thumbs-up-button').forEach(button => {
    button.addEventListener('click', () => {
        const recipeId = button.dataset.recipeId;
        handleThumbsUp(recipeId);
    });
});

document.querySelectorAll('.comment-form').forEach(form => {
    form.addEventListener('submit', event => {
        event.preventDefault();
        const recipeId = form.dataset.recipeId;
        const comment = form.querySelector('textarea').value;
        handleComment(recipeId, comment);
    });
});