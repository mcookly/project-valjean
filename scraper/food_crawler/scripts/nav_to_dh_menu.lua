-- Click button script
function click_button(splash, sel)
    splash.images_enabled = false -- This may be redundant
    btn = splash:select(sel)
    local attempt = 1
    while not btn and attempt <= 3 do
        assert(splash:wait(splash.args.wait*2))
        btn = splash:select(sel)
        attempt = attempt + 1
    end
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
    return splash:html()
end