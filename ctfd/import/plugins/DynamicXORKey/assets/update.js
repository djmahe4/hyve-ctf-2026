CTFd.plugin.run((_CTFd) => {
    const $ = _CTFd.lib.$;
    const md = _CTFd.lib.markdown();

    // Populate the form with current values
    $('#minimum-input').val(CHALLENGE_DATA.minimum);
    $('#decay-input').val(CHALLENGE_DATA.decay);
});
