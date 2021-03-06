from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Item, Review
from .forms import ProductForm


def menu(request):
    """Renders menu page"""
    items = Item.objects.all()
    query = None
    # Returns search results
    if 'q' in request.GET:
        query = request.GET['q']
        if not query:
            messages.error(request, 'Not a valid search')
            return redirect(reverse('menu'))
        queries = Q(name__icontains=query) | Q(ingredients__icontains=query)
        items = Item.objects.filter(queries)

    context = {
        'items': items,
        'show_bag': True
    }
    return render(request, 'product/menu.html', context)


def item(request, item_id):
    """Renders single item page"""
    pizza_item = Item.objects.get(id=item_id)
    context = {
        'item': pizza_item,
        'reviews': Review.objects.filter(item=pizza_item)[::-1],
        'show_bag': True
    }
    return render(request, 'product/item.html', context)


@login_required
def add_review(request, item_id):
    """Adds new item review to database"""
    title = request.POST['review__title']
    content = request.POST['review__text']
    current_user = request.user
    current_item = Item.objects.get(id=item_id)
    Review.objects.create(
        user_profile=current_user, item=current_item, title=title, content=content)
    messages.add_message(request, messages.INFO, 'New review added.')
    return redirect('item', item_id)


@login_required()
def delete_review(request, item_id, review_id):
    """Deletes item review from database"""
    review = Review.objects.get(id=review_id)
    # Check if user is allowed to see the order
    if not (str(review.user_profile) == request.user.username or request.user.is_superuser):
        messages.error(request, 'Permission denied.')
        return redirect(reverse('index'))
    review.delete()
    messages.add_message(request, messages.INFO, 'Review deleted.')
    return redirect('item', item_id)


@login_required()
def edit_review(request, review_id):
    """Modifies item review and changes it in database"""
    review = Review.objects.get(id=review_id)
    # Check if user is allowed to see the order
    if not (str(review.user_profile) == request.user.username or request.user.is_superuser):
        messages.error(request, 'Permission denied.')
        return redirect(reverse('index'))
    if request.method == 'POST':
        title = request.POST['review__title']
        content = request.POST['review__text']
        review.title = title
        review.content = content
        review.save()
        item_id = review.item.id
        messages.add_message(request, messages.INFO, 'Review updated.')
        return redirect('item', item_id)
    context = {
        'review': review,
    }
    return render(request, 'product/edit_review.html', context)


@login_required()
def add_product(request):
    """ Add a product to the store """
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect(reverse('index'))

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if request.FILES == {}:
            messages.error(request, 'Upload FAILED: Image field is mandatory!')
            return redirect(reverse('add_product'))

        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('menu'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the \
                form is valid.')
    else:
        form = ProductForm()
    context = {
        'form': form,
    }

    return render(request, 'product/add_product.html', context)


@login_required()
def edit_product(request, item_id):
    """ Edit product in the store """
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect(reverse('index'))

    product = get_object_or_404(Item, pk=item_id)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if request.POST.get('image-clear') == 'on':
            messages.error(request, 'Edit FAILED: Image field is mandatory!')
            return redirect(reverse('edit_product', args=[item_id]))

        if form.is_valid():
            form.save()
            messages.success(request, 'Successfully edited product details!')
            return redirect(reverse('menu'))
        else:
            messages.error(request, 'Failed to add product. Please ensure the \
                form is valid.')
    else:
        form = ProductForm(instance=product)
    context = {
        'form': form,
        'item': product,
    }
    return render(request, 'product/edit_product.html', context)


@login_required()
def delete_product(request, item_id):
    """ Delete an item from the database """
    if not request.user.is_superuser:
        messages.error(request, 'Permission denied.')
        return redirect(reverse('index'))
    pizza_item = get_object_or_404(Item, pk=item_id)
    pizza_item.delete()
    messages.success(request, 'Item deleted!')
    return redirect(reverse('menu'))
