const pagination = document.querySelector("#pagination");
const prevPage = document.querySelector("#pagination-previous");
const nextPage = document.querySelector("#pagination-next");
let tableRows;
let selectedPageNum;
let totalPageNums;
let maxRows = 10; // max rows per table page
let maxPageNums = 7; // max page nums in pagination bar

// called every time the table is rendered
function renderPagination(clickedPageNum) {
    tableRows = document.querySelectorAll("#tableBody > .order-in-table");
    if (tableRows.length > maxRows) {
        for (let i = 0; i < tableRows.length; i++) {
            tableRows.item(i).hidden = true;
        }
        totalPageNums = Math.ceil(tableRows.length / maxRows);
        selectedPageNum = clickedPageNum || getSelectedPageNum();
        renderPaginationBar();
        let currentRow = getCurrentRow();
        for (let i = currentRow; i < currentRow + maxRows; i++) {
            if (!tableRows.item(i)) {
                break;
            }
            tableRows.item(i).hidden = false;
        }
    } else {
        for (let i = 0; i < tableRows.length; i++) {
            tableRows.item(i).hidden = false;
        }
    }
}

// render pagination bar (can include ellipsis)
function renderPaginationBar() {
    pagination.innerHTML = "";
    prevPage.setAttribute("disabled", "");
    nextPage.setAttribute("disabled", "");
    prevPage.removeEventListener("click", onPrevPage);
    nextPage.removeEventListener("click", onNextPage);
    if (selectedPageNum != 1) {
        prevPage.removeAttribute("disabled");
        prevPage.addEventListener("click", onPrevPage);
    }
    if (selectedPageNum != totalPageNums) {
        nextPage.removeAttribute("disabled");
        nextPage.addEventListener("click", onNextPage);
    }
    // temporary; will show all page nums even if it overflows
    for (let i = 1; i <= totalPageNums; i++) {
        pagination.appendChild(getPaginationElement(i, selectedPageNum == i));
    }
}

function getPaginationElement(pageNum, isCurrent) {
    let paginationElement = document.createElement("li");
    // ellipsis
    if (!pageNum || pageNum === "...") {
        let paginationSpan = document.createElement("span");
        paginationSpan.classList.add("pagination-ellipsis");
        paginationSpan.innerText = "&hellip;";
        paginationElement.appendChild(paginationSpan);
        return paginationElement;
    }
    // page num
    let paginationLink = document.createElement("a");
    paginationLink.classList.add("pagination-link");
    if (isCurrent) {
        paginationLink.classList.add("is-current");
    }
    paginationLink.innerText = pageNum;
    paginationElement.appendChild(paginationLink);
    if (!isCurrent) {
        paginationElement.addEventListener("click", function() {
            renderPagination(pageNum);
        });
    }
    return paginationElement;
}

function getSelectedPageNum() {
    let selectedPageNum = document.querySelector("#pagination > li > .is-current")
        ? document.querySelector("#pagination > li > .is-current").innerText : 1;
    selectedPageNum = Math.max(1, selectedPageNum);
    if (selectedPageNum > totalPageNums) {
        selectedPageNum = totalPageNums;
    }
    return selectedPageNum;
}

function getCurrentRow() {
    return maxRows * (selectedPageNum - 1);
}

function onPrevPage() {
    renderPagination(Math.max(1, selectedPageNum - 1));
}

function onNextPage() {
    renderPagination(Math.min(totalPageNums, selectedPageNum + 1));
}
