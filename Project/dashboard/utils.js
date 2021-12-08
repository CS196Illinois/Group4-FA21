function product(num1, num2) {
    return parseFloat(num1) * parseFloat(num2);
}

function inCommaFormat(num) {
    num = Math.floor(parseFloat(num) * 100) / 100;
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}
