function product(num1, num2) {
    return parseFloat(num1) * parseFloat(num2);
}

function inCommaFormat(num) {
    return round(num).toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}

function round(num) {
    return Math.floor(parseFloat(num) * 100) / 100;
}
