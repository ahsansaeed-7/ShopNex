document.addEventListener("DOMContentLoaded", () => {

    const menuToggle =
        document.getElementById("menuToggle");

    const navLinks =
        document.querySelector(".nav-links");


    if (menuToggle) {

        menuToggle.addEventListener("click", () => {

            navLinks.classList.toggle("mobile-active");

        });

    }


    const wishlistButtons =
        document.querySelectorAll(".wishlist-btn");


    wishlistButtons.forEach(button => {

        button.addEventListener("click", () => {

            const icon =
                button.querySelector("i");

            icon.classList.toggle(
                "fa-regular"
            );

            icon.classList.toggle(
                "fa-solid"
            );

            button.classList.toggle(
                "active"
            );

        });

    });


    const cartButtons =
        document.querySelectorAll(".add-cart-btn");


    cartButtons.forEach(button => {

        button.addEventListener("click", () => {

            if (button.disabled) {
                return;
            }

            const originalText =
                button.innerHTML;

            button.innerHTML =
                '<i class="fa-solid fa-check"></i> Added';

            button.style.background =
                "#2788ff";


            setTimeout(() => {

                button.innerHTML =
                    originalText;

                button.style.background =
                    "";

            }, 1200);

        });

    });

});
document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menuToggle");
    const mobileMenu = document.getElementById("mobileMenu");

    if (menuToggle && mobileMenu) {

        menuToggle.addEventListener("click", function () {

            mobileMenu.classList.toggle("active");

            const icon = menuToggle.querySelector("i");

            if (mobileMenu.classList.contains("active")) {

                icon.classList.remove("fa-bars");
                icon.classList.add("fa-xmark");

            } else {

                icon.classList.remove("fa-xmark");
                icon.classList.add("fa-bars");

            }

        });

    }

});

document.addEventListener("DOMContentLoaded", function () {

    // ==========================================
    // ADD TO CART - AJAX
    // ==========================================

    document.addEventListener("submit", async function (event) {

        const form = event.target;

        if (!form.classList.contains("ajax-cart-form")) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        const button = form.querySelector("button[type='submit']");

        if (!button) {
            return;
        }

        // Prevent double clicks
        if (button.disabled) {
            return;
        }

        const originalHTML = button.innerHTML;

        button.disabled = true;

        button.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Adding...
        `;

        try {

            const response = await fetch(form.action, {

                method: "POST",

                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json"
                },

                body: new FormData(form)

            });

            const contentType = response.headers.get("content-type") || "";

            if (!response.ok) {
                throw new Error("Request failed: " + response.status);
            }

            if (!contentType.includes("application/json")) {

                const text = await response.text();

                console.error("Expected JSON but received:", text);

                throw new Error("Server did not return JSON.");

            }

            const data = await response.json();

            console.log("Cart response:", data);

            if (data.success) {

                // --------------------------------
                // UPDATE CART COUNT
                // --------------------------------

                updateCartCount(data.cart_count);


                // --------------------------------
                // BUTTON SUCCESS
                // --------------------------------

                button.innerHTML = `
                    <i class="fa-solid fa-check"></i>
                    Added to Cart
                `;

                button.classList.add("cart-added");


                // --------------------------------
                // SUCCESS MESSAGE
                // --------------------------------

                showToast(
                    data.message || "Product added to cart!",
                    "success"
                );


                // Restore button after 2 seconds

                setTimeout(function () {

                    button.innerHTML = originalHTML;

                    button.disabled = false;

                    button.classList.remove("cart-added");

                }, 2000);

            } else {

                throw new Error(
                    data.message || "Could not add product to cart."
                );

            }

        } catch (error) {

            console.error("Cart error:", error);

            button.innerHTML = originalHTML;

            button.disabled = false;

            showToast(
                error.message || "Something went wrong.",
                "error"
            );

        }

    });


    // ==========================================
    // ADD TO WISHLIST - AJAX
    // ==========================================

    document.addEventListener("submit", async function (event) {

        const form = event.target;

        if (!form.classList.contains("ajax-wishlist-form")) {
            return;
        }

        event.preventDefault();
        event.stopPropagation();

        const button = form.querySelector("button[type='submit']");

        if (!button) {
            return;
        }

        if (button.disabled) {
            return;
        }

        const originalHTML = button.innerHTML;

        button.disabled = true;

        button.innerHTML = `
            <i class="fa-solid fa-spinner fa-spin"></i>
            Adding...
        `;

        try {

            const response = await fetch(form.action, {

                method: "POST",

                headers: {
                    "X-Requested-With": "XMLHttpRequest",
                    "Accept": "application/json"
                },

                body: new FormData(form)

            });

            const contentType = response.headers.get("content-type") || "";

            if (!response.ok) {
                throw new Error("Request failed: " + response.status);
            }

            if (!contentType.includes("application/json")) {

                const text = await response.text();

                console.error("Expected JSON but received:", text);

                throw new Error("Server did not return JSON.");

            }

            const data = await response.json();

            console.log("Wishlist response:", data);

            if (data.success) {

                // --------------------------------
                // UPDATE WISHLIST COUNT
                // --------------------------------

                updateWishlistCount(data.wishlist_count);


                // --------------------------------
                // SUCCESS BUTTON
                // --------------------------------

                button.innerHTML = `
                    <i class="fa-solid fa-heart"></i>
                    Added to Wishlist
                `;

                button.classList.add("wishlist-added");


                // --------------------------------
                // TOAST
                // --------------------------------

                showToast(
                    data.message || "Added to wishlist!",
                    "success"
                );


                setTimeout(function () {

                    button.innerHTML = originalHTML;

                    button.disabled = false;

                    button.classList.remove("wishlist-added");

                }, 2000);

            } else {

                throw new Error(
                    data.message || "Could not add to wishlist."
                );

            }

        } catch (error) {

            console.error("Wishlist error:", error);

            button.innerHTML = originalHTML;

            button.disabled = false;

            showToast(
                error.message || "Something went wrong.",
                "error"
            );

        }

    });


    // ==========================================
    // UPDATE CART COUNT
    // ==========================================

    function updateCartCount(count) {

        const cartCounters = document.querySelectorAll(
            ".cart-count, #cart-count, [data-cart-count]"
        );

        cartCounters.forEach(function (counter) {

            counter.textContent = count || 0;

        });

    }


    // ==========================================
    // UPDATE WISHLIST COUNT
    // ==========================================

    function updateWishlistCount(count) {

        const wishlistCounters = document.querySelectorAll(
            ".wishlist-count, #wishlist-count, [data-wishlist-count]"
        );

        wishlistCounters.forEach(function (counter) {

            counter.textContent = count || 0;

        });

    }


    // ==========================================
    // TOAST MESSAGE
    // ==========================================

    function showToast(message, type = "success") {

        let toast = document.getElementById("shopnex-toast");

        if (!toast) {

            toast = document.createElement("div");

            toast.id = "shopnex-toast";

            document.body.appendChild(toast);

        }

        toast.textContent = message;

        toast.className = "shopnex-toast " + type;

        // Force animation restart

        void toast.offsetWidth;

        toast.classList.add("show");

        setTimeout(function () {

            toast.classList.remove("show");

        }, 3000);

    }

});



document.addEventListener("DOMContentLoaded", function () {

    const menuToggle = document.getElementById("menuToggle");
    const menuClose = document.getElementById("menuClose");
    const sideMenu = document.getElementById("sideMenu");
    const menuOverlay = document.getElementById("menuOverlay");


    function openMenu() {

        sideMenu.classList.add("active");
        menuOverlay.classList.add("active");

        document.body.style.overflow = "hidden";
    }


    function closeMenu() {

        sideMenu.classList.remove("active");
        menuOverlay.classList.remove("active");

        document.body.style.overflow = "";
    }


    menuToggle.addEventListener("click", openMenu);

    menuClose.addEventListener("click", closeMenu);

    menuOverlay.addEventListener("click", closeMenu);


    /* Close with ESC */

    document.addEventListener("keydown", function (event) {

        if (event.key === "Escape") {
            closeMenu();
        }

    });


    /* Close menu after clicking a link */

    const menuLinks = document.querySelectorAll(".menu-links a");

    menuLinks.forEach(function (link) {

        link.addEventListener("click", function () {
            closeMenu();
        });

    });

});



/* =========================================================
   SHOPNEX DARK / LIGHT MODE
========================================================= */

document.addEventListener("DOMContentLoaded", function () {

    const themeToggle = document.getElementById("themeToggle");
    const themeIcon = document.getElementById("themeIcon");
    const themeText = document.getElementById("themeText");

    if (!themeToggle) {
        return;
    }


    /* =========================================
       LOAD SAVED THEME
    ========================================= */

    const savedTheme = localStorage.getItem("shopnex-theme");


    if (savedTheme === "light") {

        document.documentElement.classList.add("light-mode");

        updateThemeUI(true);

    } else {

        document.documentElement.classList.remove("light-mode");

        updateThemeUI(false);

    }


    /* =========================================
       TOGGLE THEME
    ========================================= */

    themeToggle.addEventListener("click", function () {

        const isLight =
            document.documentElement.classList.toggle("light-mode");


        if (isLight) {

            localStorage.setItem(
                "shopnex-theme",
                "light"
            );

            updateThemeUI(true);

        } else {

            localStorage.setItem(
                "shopnex-theme",
                "dark"
            );

            updateThemeUI(false);

        }

    });


    /* =========================================
       UPDATE MENU UI
    ========================================= */

    function updateThemeUI(isLight) {

        if (isLight) {

            themeText.textContent = "Light Mode";

            themeIcon.classList.remove(
                "fa-moon"
            );

            themeIcon.classList.add(
                "fa-sun"
            );

        } else {

            themeText.textContent = "Dark Mode";

            themeIcon.classList.remove(
                "fa-sun"
            );

            themeIcon.classList.add(
                "fa-moon"
            );

        }

    }

});
document.addEventListener("DOMContentLoaded", function () {

    const filterButton =
        document.getElementById("shopnexFilterToggle");

    const filterSidebar =
        document.getElementById("filtersSidebar");

    const closeButton =
        document.getElementById("closeFilterBtn");


    if (!filterButton || !filterSidebar) {
        return;
    }


    /* CREATE BACKDROP */

    let backdrop =
        document.querySelector(".shopnex-filter-backdrop");


    if (!backdrop) {

        backdrop =
            document.createElement("div");

        backdrop.className =
            "shopnex-filter-backdrop";

        document.body.appendChild(backdrop);

    }


    /* OPEN FILTER */

    filterButton.addEventListener("click", function () {

        filterSidebar.classList.add(
            "shopnex-filter-open"
        );

        backdrop.classList.add(
            "active"
        );

        document.body.classList.add(
            "shopnex-filter-active"
        );

    });


    /* CLOSE FILTER */

    function closeFilter() {

        filterSidebar.classList.remove(
            "shopnex-filter-open"
        );

        backdrop.classList.remove(
            "active"
        );

        document.body.classList.remove(
            "shopnex-filter-active"
        );

    }


    if (closeButton) {

        closeButton.addEventListener(
            "click",
            closeFilter
        );

    }


    /* CLICK OUTSIDE */

    backdrop.addEventListener(
        "click",
        closeFilter
    );


    /* ESC KEY */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeFilter();

            }

        }
    );

});
/* ============================================================
   SHOPNEX — SEARCH + CART DRAWER + CART PAGE
   Works with:

   /cart/
   /cart/increase/<item_id>/
   /cart/decrease/<item_id>/
   /cart/remove/<item_id>/

   Cart HTML classes:
   .cart-item
   .increase-btn
   .decrease-btn
   .remove-cart-btn
   #quantity-ITEM_ID
   #item-total-ITEM_ID
============================================================ */


document.addEventListener("DOMContentLoaded", function () {

    console.log("SHOPNEX Search + Cart loaded");


    /* ============================================================
       ELEMENTS
    ============================================================ */

    const searchButton =
        document.getElementById("sxSearchButton");

    const searchPanel =
        document.getElementById("sxSearchPanel");

    const closeSearch =
        document.getElementById("sxCloseSearch");

    const searchInput =
        document.getElementById("sxSearchInput");

    const searchForm =
        document.getElementById("sxSearchForm");

    const searchResults =
        document.getElementById("sxSearchResults");


    /* ============================================================
       CART DRAWER ELEMENTS
    ============================================================ */

    const cartButton =
        document.getElementById("sxOpenCart");

    const cartDrawer =
        document.getElementById("sxCartDrawer");

    const cartOverlay =
        document.getElementById("sxCartOverlay");

    const closeCart =
        document.getElementById("sxCloseCart");

    const cartContent =
        document.getElementById("sxCartContent");

    const cartFooter =
        document.getElementById("sxCartFooter");

    const headerCartCount =
        document.getElementById("sxHeaderCartCount");

    const cartCount =
        document.getElementById("sxCartCount");

    const cartTotal =
        document.getElementById("sxCartTotal");


    /* ============================================================
       CSRF TOKEN
    ============================================================ */

    function getCSRFToken() {

        /*
         * First try cookie
         */

        const cookie =
            document.cookie
                .split("; ")
                .find(function (row) {

                    return row.startsWith(
                        "csrftoken="
                    );

                });


        if (cookie) {

            return decodeURIComponent(
                cookie.split("=")[1]
            );

        }


        /*
         * If cookie isn't available,
         * try hidden CSRF input.
         */

        const csrfInput =
            document.querySelector(
                "[name=csrfmiddlewaretoken]"
            );


        if (csrfInput) {

            return csrfInput.value;

        }


        return "";

    }


    /* ============================================================
       PRICE FORMAT
    ============================================================ */

    function formatPrice(value) {

        return Number(value || 0)
            .toLocaleString(
                "en-PK",
                {
                    minimumFractionDigits: 2,
                    maximumFractionDigits: 2
                }
            );

    }


    /* ============================================================
       SEARCH
    ============================================================ */

    if (searchButton && searchPanel) {

        searchButton.addEventListener(
            "click",
            function () {

                searchPanel.classList.add(
                    "active"
                );


                setTimeout(
                    function () {

                        if (searchInput) {

                            searchInput.focus();

                        }

                    },
                    200
                );

            }
        );

    }


    /* ============================================================
       CLOSE SEARCH
    ============================================================ */

    if (closeSearch) {

        closeSearch.addEventListener(
            "click",
            function () {

                searchPanel.classList.remove(
                    "active"
                );


                if (searchInput) {

                    searchInput.value = "";

                }


                showAllProducts();


                if (searchResults) {

                    searchResults.innerHTML = "";

                }

            }
        );

    }


    /* ============================================================
       LIVE SEARCH
    ============================================================ */

    if (searchInput) {

        searchInput.addEventListener(
            "input",
            function () {

                const value =
                    this.value
                        .trim()
                        .toLowerCase();


                const products =
                    document.querySelectorAll(
                        ".product-card"
                    );


                let found = 0;


                products.forEach(
                    function (product) {

                        const nameElement =
                            product.querySelector(
                                "h3"
                            );


                        const categoryElement =
                            product.querySelector(
                                ".product-category"
                            );


                        const name =
                            nameElement
                                ? nameElement
                                    .textContent
                                    .trim()
                                    .toLowerCase()
                                : "";


                        const category =
                            categoryElement
                                ? categoryElement
                                    .textContent
                                    .trim()
                                    .toLowerCase()
                                : "";


                        if (
                            value === "" ||
                            name.includes(value) ||
                            category.includes(value)
                        ) {

                            product.style.display =
                                "";

                            found++;

                        }

                        else {

                            product.style.display =
                                "none";

                        }

                    }
                );


                /*
                 * NO RESULT MESSAGE
                 */

                let noResult =
                    document.getElementById(
                        "sxSearchNoResult"
                    );


                if (
                    value !== "" &&
                    found === 0
                ) {

                    if (!noResult) {

                        noResult =
                            document.createElement(
                                "div"
                            );


                        noResult.id =
                            "sxSearchNoResult";


                        noResult.innerHTML = `
                            <i class="fa-solid fa-box-open"></i>
                            <p>No products found</p>
                        `;


                        const grid =
                            document.querySelector(
                                ".products-grid"
                            );


                        if (grid) {

                            grid.appendChild(
                                noResult
                            );

                        }

                    }

                }

                else {

                    if (noResult) {

                        noResult.remove();

                    }

                }

            }
        );

    }


    /* ============================================================
       SEARCH FORM
    ============================================================ */

    if (searchForm) {

        searchForm.addEventListener(
            "submit",
            function (event) {

                const value =
                    searchInput
                        ? searchInput.value.trim()
                        : "";


                if (value === "") {

                    event.preventDefault();

                }

            }
        );

    }


    /* ============================================================
       SHOW ALL PRODUCTS
    ============================================================ */

    function showAllProducts() {

        const products =
            document.querySelectorAll(
                ".product-card"
            );


        products.forEach(
            function (product) {

                product.style.display = "";

            }
        );


        const noResult =
            document.getElementById(
                "sxSearchNoResult"
            );


        if (noResult) {

            noResult.remove();

        }

    }


    /* ============================================================
       CART DRAWER — OPEN
    ============================================================ */

    if (cartButton) {

        cartButton.addEventListener(
            "click",
            function () {

                openCart();

            }
        );

    }


    function openCart() {

        if (!cartDrawer) {

            console.error(
                "Cart drawer not found"
            );

            return;

        }


        cartDrawer.classList.add(
            "active"
        );


        if (cartOverlay) {

            cartOverlay.classList.add(
                "active"
            );

        }


        document.body.classList.add(
            "sx-cart-open"
        );


        loadCart();

    }


    /* ============================================================
       CART DRAWER — CLOSE
    ============================================================ */

    function closeCartDrawer() {

        if (cartDrawer) {

            cartDrawer.classList.remove(
                "active"
            );

        }


        if (cartOverlay) {

            cartOverlay.classList.remove(
                "active"
            );

        }


        document.body.classList.remove(
            "sx-cart-open"
        );

    }


    if (closeCart) {

        closeCart.addEventListener(
            "click",
            closeCartDrawer
        );

    }


    if (cartOverlay) {

        cartOverlay.addEventListener(
            "click",
            closeCartDrawer
        );

    }


    /* ============================================================
       ESC KEY
    ============================================================ */

    document.addEventListener(
        "keydown",
        function (event) {

            if (event.key === "Escape") {

                closeCartDrawer();


                if (searchPanel) {

                    searchPanel.classList.remove(
                        "active"
                    );

                }

            }

        }
    );


    /* ============================================================
       LOAD CART DRAWER
    ============================================================ */

    function loadCart() {

        if (!cartContent) {

            return;

        }


        cartContent.innerHTML = `
            <div class="sx-cart-loading">
                <i class="fa-solid fa-spinner fa-spin"></i>
                <p>Loading cart...</p>
            </div>
        `;


        fetch(
            "/cart/",
            {
                method: "GET",

                headers: {
                    "X-Requested-With":
                        "XMLHttpRequest"
                }
            }
        )

        .then(
            function (response) {

                if (!response.ok) {

                    throw new Error(
                        "Cart loading failed"
                    );

                }


                return response.text();

            }
        )

        .then(
            function (html) {

                const parser =
                    new DOMParser();


                const doc =
                    parser.parseFromString(
                        html,
                        "text/html"
                    );


                const items =
                    doc.querySelectorAll(
                        ".cart-item"
                    );


                console.log(
                    "Cart items found:",
                    items.length
                );


                if (!items.length) {

                    showEmptyCart();

                    return;

                }


                renderCart(items);

            }
        )

        .catch(
            function (error) {

                console.error(
                    "SHOPNEX CART ERROR:",
                    error
                );


                showCartError();

            }
        );

    }


    /* ============================================================
       RENDER CART DRAWER
    ============================================================ */

    function renderCart(items) {

        let html = "";

        let cartTotalValue = 0;

        let cartQuantity = 0;


        items.forEach(
            function (item) {


                /* ================================================
                   CART ITEM ID
                ================================================= */

                let itemId =
                    item.dataset.itemId
                    || item.getAttribute(
                        "data-id"
                    )
                    || "";


                /*
                 * Try increase URL
                 */

                if (!itemId) {

                    const increaseLink =
                        item.querySelector(
                            'a[href*="/cart/increase/"]'
                        );


                    if (increaseLink) {

                        const match =
                            increaseLink
                                .getAttribute(
                                    "href"
                                )
                                .match(
                                    /\/cart\/increase\/(\d+)\//
                                );


                        if (match) {

                            itemId =
                                match[1];

                        }

                    }

                }


                /*
                 * Try decrease URL
                 */

                if (!itemId) {

                    const decreaseLink =
                        item.querySelector(
                            'a[href*="/cart/decrease/"]'
                        );


                    if (decreaseLink) {

                        const match =
                            decreaseLink
                                .getAttribute(
                                    "href"
                                )
                                .match(
                                    /\/cart\/decrease\/(\d+)\//
                                );


                        if (match) {

                            itemId =
                                match[1];

                        }

                    }

                }


                /* ================================================
                   PRODUCT NAME
                ================================================= */

                const nameElement =
                    item.querySelector(
                        ".cart-product-name"
                    )
                    ||
                    item.querySelector(
                        ".cart-product-info h2"
                    )
                    ||
                    item.querySelector(
                        "h2"
                    )
                    ||
                    item.querySelector(
                        "h3"
                    )
                    ||
                    item.querySelector(
                        "h4"
                    );


                const productName =
                    nameElement
                        ? nameElement
                            .textContent
                            .trim()
                        : "Product";


                /* ================================================
                   IMAGE
                ================================================= */

                const imageElement =
                    item.querySelector(
                        "img"
                    );


                const image =
                    imageElement
                        ? imageElement.getAttribute(
                            "src"
                        )
                        : "";


                /* ================================================
                   QUANTITY
                ================================================= */

                let quantity = 1;


                const quantityInput =
                    item.querySelector(
                        "input[type='number']"
                    );


                const quantityElement =
                    item.querySelector(
                        ".cart-quantity strong"
                    )
                    ||
                    item.querySelector(
                        ".cart-qty"
                    )
                    ||
                    item.querySelector(
                        ".quantity"
                    );


                if (quantityInput) {

                    quantity =
                        parseInt(
                            quantityInput.value
                        ) || 1;

                }

                else if (quantityElement) {

                    quantity =
                        parseInt(
                            quantityElement
                                .textContent
                        ) || 1;

                }


                /* ================================================
                   PRICE
                ================================================= */

                const priceElement =
                    item.querySelector(
                        ".cart-price"
                    )
                    ||
                    item.querySelector(
                        ".current-price"
                    );


                let price = 0;


                if (priceElement) {
                   const priceText = priceElement.textContent.trim();

    price = parseFloat(
        priceText.replace(/Rs\.?/gi, "").replace(/,/g, "").trim()
    ) || 0;

                }


                /* ================================================
                   ITEM TOTAL
                ================================================= */

                const itemTotal =
                    price * quantity;


                cartTotalValue +=
                    itemTotal;


                cartQuantity +=
                    quantity;


                /* ================================================
                   SIDEBAR ITEM
                ================================================= */

                html += `

                    <div
                        class="sx-mini-cart-item"
                        data-item-id="${itemId}"
                    >

                        <div class="sx-mini-cart-image">

                            ${
                                image

                                ?

                                `<img
                                    src="${image}"
                                    alt="${escapeHTML(
                                        productName
                                    )}"
                                >`

                                :

                                `<i class="fa-solid fa-image"></i>`
                            }

                        </div>


                        <div class="sx-mini-cart-info">

                            <h4>
                                ${escapeHTML(
                                    productName
                                )}
                            </h4>


                            <span class="sx-mini-cart-price">
                                Rs.${formatPrice(price)}
                            </span>


                            <div
                                class="sx-mini-cart-actions"
                            >

                                <button
                                    type="button"
                                    class="sx-qty-btn"
                                    data-action="decrease"
                                    data-item-id="${itemId}"
                                    ${
                                        !itemId
                                            ? "disabled"
                                            : ""
                                    }
                                >
                                    −
                                </button>


                                <span class="sx-qty">
                                    ${quantity}
                                </span>


                                <button
                                    type="button"
                                    class="sx-qty-btn"
                                    data-action="increase"
                                    data-item-id="${itemId}"
                                    ${
                                        !itemId
                                            ? "disabled"
                                            : ""
                                    }
                                >
                                    +
                                </button>

                            </div>

                        </div>


                        <button
                            type="button"
                            class="sx-remove-item"
                            data-item-id="${itemId}"
                            ${
                                !itemId
                                    ? "disabled"
                                    : ""
                            }
                            aria-label="Remove product"
                        >

                            <i
                                class="fa-solid fa-trash"
                            ></i>

                        </button>

                    </div>

                `;

            }
        );


        cartContent.innerHTML =
            html;


        /*
         * Correct total
         */

        if (cartTotal) {

            cartTotal.textContent =
                "Rs." +
                formatPrice(
                    cartTotalValue
                );

        }


        /*
         * Correct quantity count
         */

        updateCartCount(
            cartQuantity
        );


        attachCartButtons();

    }


    /* ============================================================
       DRAWER BUTTON EVENTS
    ============================================================ */

    function attachCartButtons() {

        const quantityButtons =
            cartContent.querySelectorAll(
                ".sx-qty-btn"
            );


        quantityButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const itemId =
                            this.dataset.itemId;


                        const action =
                            this.dataset.action;


                        if (!itemId) {

                            console.error(
                                "Cart item ID missing"
                            );

                            return;

                        }


                        updateDrawerQuantity(
                            itemId,
                            action
                        );

                    }
                );

            }
        );


        const removeButtons =
            cartContent.querySelectorAll(
                ".sx-remove-item"
            );


        removeButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const itemId =
                            this.dataset.itemId;


                        if (!itemId) {

                            return;

                        }


                        removeDrawerItem(
                            itemId
                        );

                    }
                );

            }
        );

    }


    /* ============================================================
       DRAWER QUANTITY UPDATE
    ============================================================ */

    function updateDrawerQuantity(
        itemId,
        action
    ) {

        let url = "";


        if (
            action === "increase"
        ) {

            url =
                "/cart/increase/" +
                itemId +
                "/";

        }

        else if (
            action === "decrease"
        ) {

            url =
                "/cart/decrease/" +
                itemId +
                "/";

        }

        else {

            return;

        }


        const buttons =
            cartContent.querySelectorAll(
                `.sx-qty-btn[data-item-id="${itemId}"]`
            );


        buttons.forEach(
            function (button) {

                button.disabled = true;

            }
        );


        fetch(
            url,
            {

                method: "POST",

                headers: {

                    "X-CSRFToken":
                        getCSRFToken(),

                    "X-Requested-With":
                        "XMLHttpRequest"

                }

            }
        )

        .then(
            function (response) {

                if (!response.ok) {

                    throw new Error(
                        "Quantity update failed"
                    );

                }


                return response.json();

            }
        )

        .then(
            function (data) {

                console.log(
                    "Drawer quantity response:",
                    data
                );


                if (!data.success) {

                    throw new Error(
                        data.message ||
                        "Unable to update cart"
                    );

                }


                /*
                 * Reload drawer so all values
                 * stay synchronized.
                 */

                loadCart();


                /*
                 * Update header count
                 */

                if (
                    typeof data.cart_count !==
                    "undefined"
                ) {

                    updateCartCount(
                        data.cart_count
                    );

                }

            }
        )

        .catch(
            function (error) {

                console.error(
                    "Drawer quantity error:",
                    error
                );


                loadCart();

            }
        );

    }


    /* ============================================================
       DRAWER REMOVE
    ============================================================ */

    function removeDrawerItem(itemId) {

        const formData =
            new FormData();


        const csrfToken =
            getCSRFToken();


        formData.append(
            "csrfmiddlewaretoken",
            csrfToken
        );


        fetch(
            "/cart/remove/" +
            itemId +
            "/",
            {

                method: "POST",

                body: formData,

                headers: {

                    "X-CSRFToken":
                        csrfToken,

                    "X-Requested-With":
                        "XMLHttpRequest"

                }

            }
        )

        .then(
            function (response) {

                if (!response.ok) {

                    throw new Error(
                        "Remove failed"
                    );

                }


                return response.json();

            }
        )

        .then(
            function (data) {

                if (!data.success) {

                    throw new Error(
                        data.message ||
                        "Unable to remove item"
                    );

                }


                loadCart();


                if (
                    typeof data.cart_count !==
                    "undefined"
                ) {

                    updateCartCount(
                        data.cart_count
                    );

                }

            }
        )

        .catch(
            function (error) {

                console.error(
                    "Remove error:",
                    error
                );


                loadCart();

            }
        );

    }


    /* ============================================================
       EMPTY CART DRAWER
    ============================================================ */

    function showEmptyCart() {

        cartContent.innerHTML = `

            <div class="sx-empty-cart">

                <div class="sx-empty-cart-icon">

                    <i
                        class="fa-solid fa-cart-shopping"
                    ></i>

                </div>


                <h3>
                    Your cart is empty
                </h3>


                <p>
                    Add some products to see them here.
                </p>


                <button
                    type="button"
                    class="sx-continue-shopping"
                    id="sxContinueShopping"
                >
                    Continue Shopping
                </button>

            </div>

        `;


        if (cartTotal) {

            cartTotal.textContent =
                "Rs.0.00";

        }


        updateCartCount(0);


        const continueButton =
            document.getElementById(
                "sxContinueShopping"
            );


        if (continueButton) {

            continueButton.addEventListener(
                "click",
                closeCartDrawer
            );

        }

    }


    /* ============================================================
       CART ERROR
    ============================================================ */

    function showCartError() {

        cartContent.innerHTML = `

            <div class="sx-empty-cart">

                <div class="sx-empty-cart-icon">

                    <i
                        class="fa-solid fa-triangle-exclamation"
                    ></i>

                </div>


                <h3>
                    Unable to load cart
                </h3>


                <p>
                    Please refresh the page and try again.
                </p>

            </div>

        `;

    }


    /* ============================================================
       UPDATE CART COUNT
    ============================================================ */

    function updateCartCount(count) {

        if (headerCartCount) {

            headerCartCount.textContent =
                count;

        }


        if (cartCount) {

            cartCount.textContent =
                "(" +
                count +
                ")";

        }

    }


    /* ============================================================
       ============================================================
       FULL CART PAGE
       ============================================================
    ============================================================ */


    /*
     * This part works with your cart.html:
     *
     * .increase-btn
     * .decrease-btn
     * .remove-cart-btn
     * #quantity-ID
     * #item-total-ID
     * #cart-item-ID
     */


    /* ============================================================
       UPDATE FULL CART TOTAL
    ============================================================ */

    function updateFullCartTotal(
        total
    ) {

        const formatted =
            "Rs. " +
            formatPrice(total);


        /*
         * Your current HTML does not have
         * these IDs, so update visible
         * totals directly.
         */


        const totalElements =
            document.querySelectorAll(
                ".cart-total strong"
            );


        totalElements.forEach(
            function (element) {

                element.textContent =
                    formatted;

            }
        );


        /*
         * Summary subtotal
         */

        const summaryRows =
            document.querySelectorAll(
                ".summary-row"
            );


        summaryRows.forEach(
            function (row) {

                const label =
                    row.querySelector(
                        "span"
                    );


                if (
                    label &&
                    label.textContent
                        .trim()
                        .toLowerCase()
                        === "subtotal"
                ) {

                    const strong =
                        row.querySelector(
                            "strong"
                        );


                    if (strong) {

                        strong.textContent =
                            formatted;

                    }

                }

            }
        );

    }


    /* ============================================================
       UPDATE FULL CART ITEM TOTAL
    ============================================================ */

    function updateFullCartItemTotal(
        itemId,
        total
    ) {

        const element =
            document.getElementById(
                "item-total-" +
                itemId
            );


        if (!element) {

            console.warn(
                "Item total element not found:",
                itemId
            );

            return;

        }


        element.textContent =
            "Rs. " +
            formatPrice(total);

    }


    /* ============================================================
       UPDATE FULL CART QUANTITY
    ============================================================ */

    function updateFullCartQuantity(
        itemId,
        quantity
    ) {

        const element =
            document.getElementById(
                "quantity-" +
                itemId
            );


        if (!element) {

            console.warn(
                "Quantity element not found:",
                itemId
            );

            return;

        }


        element.textContent =
            quantity;

    }


    /* ============================================================
       INCREASE FULL CART
    ============================================================ */

    document
        .querySelectorAll(
            ".increase-btn"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const itemId =
                            this.dataset.id;


                        if (!itemId) {

                            console.error(
                                "Increase button has no data-id"
                            );

                            return;

                        }


                        /*
                         * Disable both buttons temporarily
                         */

                        setFullCartButtonsDisabled(
                            itemId,
                            true
                        );


                        fetch(
                            "/cart/increase/" +
                            itemId +
                            "/",
                            {

                                method: "POST",

                                headers: {

                                    "X-CSRFToken":
                                        getCSRFToken(),

                                    "X-Requested-With":
                                        "XMLHttpRequest"

                                }

                            }
                        )

                        .then(
                            function (response) {

                                if (!response.ok) {

                                    throw new Error(
                                        "Increase failed"
                                    );

                                }


                                return response.json();

                            }
                        )

                        .then(
                            function (data) {

                                console.log(
                                    "Increase response:",
                                    data
                                );


                                if (!data.success) {

                                    alert(
                                        data.message ||
                                        "Unable to increase quantity."
                                    );


                                    return;

                                }


                                /*
                                 * Update quantity
                                 */

                                updateFullCartQuantity(
                                    itemId,
                                    data.quantity
                                );


                                /*
                                 * Update item total
                                 */

                                updateFullCartItemTotal(
                                    itemId,
                                    data.item_total
                                );


                                /*
                                 * Update entire cart total
                                 */

                                updateFullCartTotal(
                                    data.cart_total
                                );


                                /*
                                 * Update navbar count
                                 */

                                if (
                                    typeof data.cart_count !==
                                    "undefined"
                                ) {

                                    updateCartCount(
                                        data.cart_count
                                    );

                                }

                            }
                        )

                        .catch(
                            function (error) {

                                console.error(
                                    "Increase error:",
                                    error
                                );

                            }
                        )

                        .finally(
                            function () {

                                setFullCartButtonsDisabled(
                                    itemId,
                                    false
                                );

                            }
                        );

                    }
                );

            }
        );


    /* ============================================================
       DECREASE FULL CART
    ============================================================ */

    document
        .querySelectorAll(
            ".decrease-btn"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const itemId =
                            this.dataset.id;


                        if (!itemId) {

                            console.error(
                                "Decrease button has no data-id"
                            );

                            return;

                        }


                        setFullCartButtonsDisabled(
                            itemId,
                            true
                        );


                        fetch(
                            "/cart/decrease/" +
                            itemId +
                            "/",
                            {

                                method: "POST",

                                headers: {

                                    "X-CSRFToken":
                                        getCSRFToken(),

                                    "X-Requested-With":
                                        "XMLHttpRequest"

                                }

                            }
                        )

                        .then(
                            function (response) {

                                if (!response.ok) {

                                    throw new Error(
                                        "Decrease failed"
                                    );

                                }


                                return response.json();

                            }
                        )

                        .then(
                            function (data) {

                                console.log(
                                    "Decrease response:",
                                    data
                                );


                                if (!data.success) {

                                    alert(
                                        data.message ||
                                        "Unable to decrease quantity."
                                    );


                                    return;

                                }


                                /*
                                 * If quantity reached zero,
                                 * Django may delete item.
                                 */

                                if (data.deleted) {

                                    removeFullCartItem(
                                        itemId
                                    );


                                    updateFullCartTotal(
                                        data.cart_total
                                    );


                                    updateCartCount(
                                        data.cart_count ||
                                        0
                                    );


                                    return;

                                }


                                /*
                                 * Update quantity
                                 */

                                updateFullCartQuantity(
                                    itemId,
                                    data.quantity
                                );


                                /*
                                 * Update item total
                                 */

                                updateFullCartItemTotal(
                                    itemId,
                                    data.item_total
                                );


                                /*
                                 * Update cart total
                                 */

                                updateFullCartTotal(
                                    data.cart_total
                                );


                                /*
                                 * Update header count
                                 */

                                if (
                                    typeof data.cart_count !==
                                    "undefined"
                                ) {

                                    updateCartCount(
                                        data.cart_count
                                    );

                                }

                            }
                        )

                        .catch(
                            function (error) {

                                console.error(
                                    "Decrease error:",
                                    error
                                );

                            }
                        )

                        .finally(
                            function () {

                                setFullCartButtonsDisabled(
                                    itemId,
                                    false
                                );

                            }
                        );

                    }
                );

            }
        );


    /* ============================================================
       REMOVE FULL CART ITEM
    ============================================================ */

    document
        .querySelectorAll(
            ".remove-cart-btn"
        )
        .forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function () {

                        const itemId =
                            this.dataset.id;


                        if (!itemId) {

                            console.error(
                                "Remove button has no data-id"
                            );

                            return;

                        }


                        const confirmed =
                            confirm(
                                "Remove this product from your cart?"
                            );


                        if (!confirmed) {

                            return;

                        }


                        const csrfToken =
                            getCSRFToken();


                        setFullCartButtonsDisabled(
                            itemId,
                            true
                        );


                        fetch(
                            "/cart/remove/" +
                            itemId +
                            "/",
                            {

                                method: "POST",

                                headers: {

                                    "X-CSRFToken":
                                        csrfToken,

                                    "X-Requested-With":
                                        "XMLHttpRequest"

                                }

                            }
                        )

                        .then(
                            function (response) {

                                if (!response.ok) {

                                    throw new Error(
                                        "Remove failed"
                                    );

                                }


                                return response.json();

                            }
                        )

                        .then(
                            function (data) {

                                console.log(
                                    "Remove response:",
                                    data
                                );


                                if (!data.success) {

                                    alert(
                                        data.message ||
                                        "Unable to remove product."
                                    );


                                    return;

                                }


                                removeFullCartItem(
                                    itemId
                                );


                                updateFullCartTotal(
                                    data.cart_total
                                );


                                updateCartCount(
                                    data.cart_count ||
                                    0
                                );

                            }
                        )

                        .catch(
                            function (error) {

                                console.error(
                                    "Remove error:",
                                    error
                                );

                            }
                        );

                    }
                );

            }
        );


    /* ============================================================
       DISABLE FULL CART BUTTONS
    ============================================================ */

    function setFullCartButtonsDisabled(
        itemId,
        disabled
    ) {

        const item =
            document.getElementById(
                "cart-item-" +
                itemId
            );


        if (!item) {

            return;

        }


        const buttons =
            item.querySelectorAll(
                ".quantity-btn, .remove-cart-btn"
            );


        buttons.forEach(
            function (button) {

                button.disabled =
                    disabled;

                if (disabled) {

                    button.style.pointerEvents =
                        "none";

                    button.style.opacity =
                        "0.6";

                }

                else {

                    button.style.pointerEvents =
                        "";

                    button.style.opacity =
                        "";

                }

            }
        );

    }


    /* ============================================================
       REMOVE FULL CART ITEM FROM PAGE
    ============================================================ */

    function removeFullCartItem(
        itemId
    ) {

        const item =
            document.getElementById(
                "cart-item-" +
                itemId
            );


        if (!item) {

            return;

        }


        item.style.opacity =
            "0";

        item.style.transform =
            "translateX(30px)";

        item.style.transition =
            "all 0.25s ease";


        setTimeout(
            function () {

                item.remove();


                checkFullCartEmpty();

            },
            250
        );

    }


    /* ============================================================
       CHECK FULL CART EMPTY
    ============================================================ */

    function checkFullCartEmpty() {

        const items =
            document.querySelectorAll(
                ".cart-item"
            );


        if (
            items.length === 0
        ) {

            /*
             * Reload the page so your existing
             * Django empty-cart section appears.
             */

            window.location.reload();

        }

    }


    /* ============================================================
       ESCAPE HTML
    ============================================================ */

    function escapeHTML(text) {

        const div =
            document.createElement(
                "div"
            );


        div.textContent =
            text;


        return div.innerHTML;

    }


    /* ============================================================
       INITIAL CART COUNT
    ============================================================ */

    /*
     * Only load drawer cart if the drawer
     * exists in base.html.
     */

    if (
        cartContent &&
        cartDrawer
    ) {

        loadCart();

    }


});
