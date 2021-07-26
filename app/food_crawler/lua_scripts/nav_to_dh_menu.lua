-- Click button script
function click_button(splash, sel)
    btn = splash:select(sel)
    btn:mouse_click()
    assert(splash:wait(splash.args.wait))
end

function main(splash, args)
    -- Navigates to the meal selection page to extract CSS selectors
    splash.images_enabled = false
    assert(splash:go(splash.args.url))
    assert(splash:wait(splash.args.wait))
    -- Navigate to meal list menu through 2 button clicks
    click_button(splash, splash.args.dh)
    click_button(splash, splash.args.fwd_btn)
    return {
        html = splash:html(),
        png = splash:png() -- For debug purposes only
    }
end