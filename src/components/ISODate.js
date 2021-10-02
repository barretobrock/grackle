

function getISODate(date) {
    if(date == null) {
        return ''
    }
    return date.getFullYear() + '-' + parseInt(date.getMonth() + 1) + '-' + date.getDate();
}

export default getISODate;